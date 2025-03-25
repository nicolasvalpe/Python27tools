import numpy as np
import gdal
import ogr
from sklearn import metrics
import matplotlib.pyplot as plt
import geopandas as gpd


#folder path
dir=r"D:\GEOMATICA\Proyecto\Imagenes\Datos_Entrenamiento\2024"
image = dir+'\\Classified_2024.tif'

driverTiff = gdal.GetDriverByName('GTiff')
naip_ds = gdal.Open(image)

test_fn = dir+"\\test.shp"
test_ds = ogr.Open(test_fn)
lyr = test_ds.GetLayer()
driver = gdal.GetDriverByName('MEM')
target_ds = driver.Create('', naip_ds.RasterXSize, naip_ds.RasterYSize, 1, gdal.GDT_UInt16)
target_ds.SetGeoTransform(naip_ds.GetGeoTransform())
target_ds.SetProjection(naip_ds.GetProjection())
options = ['ATTRIBUTE=CLC']
gdal.RasterizeLayer(target_ds, [1], lyr, options=options)

truth = target_ds.GetRasterBand(1).ReadAsArray()

pred_ds = gdal.Open(dir+"\\Classified_2024.tif")
pred = pred_ds.GetRasterBand(1).ReadAsArray()

idx = np.nonzero(truth)

#matrix confusion
cm = metrics.confusion_matrix(truth[idx], pred[idx])

#Lables from data train 
gdf=gpd.read_file(test_fn)
class_names = gdf['Leyenda'].unique()
#class_names=["99","111","231","311","323","331","511","512"]

#Classification report
print("Classification report: ")
report=metrics.classification_report(truth[idx], pred[idx],target_names=class_names,digits=4)
print(report)


#Cohen's Kappa  
dg=cm.diagonal(); sumdg=sum(dg)
sumX=sum(cm.sum(axis=0)); sumY=sum(cm.sum(axis=1))
#Summarize total vectors 
SumMargin=sum(cm.sum(axis=0)*cm.sum(axis=1))
Kappa=((sumX*sumdg)-SumMargin)/(sumX**2-SumMargin)
print("Cohen's Kappa    ",round(Kappa,3))

#plot Confusion matrix
cm_display = metrics.ConfusionMatrixDisplay(confusion_matrix = cm,display_labels = class_names)
cm_display.plot(cmap="Greens")
cm_display.ax_.set_title("Matriz de confusión")
plt.show()
