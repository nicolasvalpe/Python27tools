import numpy as np
import gdal
from skimage import exposure
from skimage.segmentation import quickshift, slic
from sklearn.ensemble import RandomForestClassifier
import time
import scipy
import gdal
import ogr

dir = r"E:\TOPOGRAFIA\MDA\Proyecto Retamo\Codigo_RF"

driverTiff = gdal.GetDriverByName('GTiff')
image=dir+"\\Neusa_PanMul.tif"
img = gdal.Open(image)  #-------> Name of image
nbands = img.RasterCount
band_data = []
print('bands', img.RasterCount, 'rows', img.RasterYSize, 'columns', img.RasterXSize)
YSize=img.RasterYSize; XSize=img.RasterXSize

for i in range(1, nbands+1):
    band = img.GetRasterBand(i).ReadAsArray()
    band_data.append(band)
band_data = np.dstack(band_data)
Gtransform=img.GetGeoTransform()
Gprojection=img.GetProjectionRef()

# scale image values from 0.0 - 1.0
img0 = exposure.rescale_intensity(band_data)

# do segmentation multiple options with quickshift and slic
seg_start = time.time()
# segments = quickshift(img, convert2lab=False)
segments = quickshift(img0, ratio=0.9, convert2lab=False)
# segments = quickshift(img, ratio=0.99, max_dist=5, convert2lab=False)
# segments = slic(img, n_segments=100000, compactness=0.1)
# segments = slic(img, n_segments=500000, compactness=0.01)
# segments = slic(img, n_segments=500000, compactness=1)

print('segments complete', time.time() - seg_start)

#staticts for segments
def segment_features(segment_pixels):
    features = []
    npixels, nbands = segment_pixels.shape
    for b in range(nbands):
        stats = scipy.stats.describe(segment_pixels[:, b])
        band_stats = list(stats.minmax) + list(stats)[2:]
        if npixels == 1:
            # in this case the variance = nan, change it 0.0
            band_stats[3] = 0.0
        features += band_stats
    return features

segment_ids = np.unique(segments)
objects = []
object_ids = []
for id in segment_ids:
    segment_pixels = img0[segments == id]
    object_features = segment_features(segment_pixels)
    objects.append(object_features)
    object_ids.append(id)

# save segments to raster
segments_fn = dir+"\\segments.tif"
segments_ds = driverTiff.Create(segments_fn, XSize, YSize,
                                1, gdal.GDT_Float32)
segments_ds.SetGeoTransform(Gtransform)
segments_ds.SetProjection(Gprojection)
segments_ds.GetRasterBand(1).WriteArray(segments)
segments_ds = None  
print("Segments save to file")


#Rasterize Training Data  -------------------------------------------------------------------

#open raster data with gdal
img2 = gdal.Open(image)  #-------> Name of image
YSize=img2.RasterYSize; XSize=img2.RasterXSize
Gtransform=img2.GetGeoTransform()
Gprojection=img2.GetProjectionRef()

# open the points file to use for training data
train_file = dir+"\\Entrenamiento\\train.shp"
train_ds = ogr.Open(train_file)
lyr = train_ds.GetLayer()

# create a new raster layer in memory
driver = gdal.GetDriverByName('MEM')
target_ds = driver.Create('', XSize,YSize, 1, gdal.GDT_UInt16)
target_ds.SetGeoTransform(Gtransform)
target_ds.SetProjection(Gprojection)

# rasterize the training points
options = ['ATTRIBUTE=class']
gdal.RasterizeLayer(target_ds, [1], lyr, options=options)
# retrieve the rasterized data and print basic stats
data = target_ds.GetRasterBand(1).ReadAsArray()
print('min', data.min(), 'max', data.max(), 'mean', data.mean())


ground_truth = target_ds.GetRasterBand(1).ReadAsArray()

classes = np.unique(ground_truth)[1:]
print('class values', classes)

segments_per_class = {}

for klass in classes:
    segments_of_class = segments[ground_truth == klass]
    segments_per_class[klass] = set(segments_of_class)
    print("Training segments for class", klass, ":", len(segments_of_class))

intersection = set()
accum = set()

for class_segments in segments_per_class.values():
    intersection |= accum.intersection(class_segments)
    accum |= class_segments
assert len(intersection) == 0, "Segment(s) represent multiple classes"


#Clasify image

train_img = np.copy(segments)
threshold = train_img.max() + 1

for klass in classes:
    class_label = threshold + klass
    for segment_id in segments_per_class[klass]:
        train_img[train_img == segment_id] = class_label

train_img[train_img <= threshold] = 0
train_img[train_img > threshold] -= threshold

training_objects = []
training_labels = []

for klass in classes:
    class_train_object = [v for i, v in enumerate(objects) if segment_ids[i] in segments_per_class[klass]]
    training_labels += [klass] * len(class_train_object)
    training_objects += class_train_object
    print('Training objects for class', klass, ':', len(class_train_object))

classifier = RandomForestClassifier(n_jobs=-1)
classifier.fit(training_objects, training_labels)
print('Fitting Random Forest Classifier')
predicted = classifier.predict(objects)
print('Predicting Classifications')

clf = np.copy(segments)
for segment_id, klass in zip(segment_ids, predicted):
    clf[clf == segment_id] = klass

print('Prediction applied to numpy array')

mask = np.sum(img0, axis=2)
mask[mask > 0.0] = 1.0
mask[mask == 0.0] = -1.0
clf = np.multiply(clf, mask)
clf[clf < 0] = -9999.0

print('Saving classificaiton to raster with gdal')

clfds = driverTiff.Create((dir+"\\classified_RF.tif"), XSize, YSize,
                          1, gdal.GDT_Float32)
clfds.SetGeoTransform(Gtransform)
clfds.SetProjection(Gprojection)
clfds.GetRasterBand(1).SetNoDataValue(-9999.0)
clfds.GetRasterBand(1).WriteArray(clf)
clfds = None

print('Done!')
