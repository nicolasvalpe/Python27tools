import numpy as np
import geopandas as gpd
import pandas as pd

dir=r"D:\PROYECTOS 2024\DAVID ALZATE\Clasificacion\Muestras_2024.shp"
# read shapefile to geopandas geodataframe
gdf = gpd.read_file(dir+"\\Clases.shp")
# get names of land cover classes/labels
class_names = gdf['Clase'].unique()   #------> Set number of atribute
print('class names', class_names)
# create a unique id (integer) for each land cover class/label
class_ids = np.arange(class_names.size) + 1
print('class ids', class_ids)

# create a pandas data frame of the labels and ids and save to csv

df = pd.DataFrame({'label': class_names, 'id': class_ids})
df.to_csv(dir+"\\class_data.csv")
print('gdf without ids', gdf.head())

# add a new column to geodatafame with the id for each class/label
gdf['id'] = gdf['Clase'].map(dict(zip(class_names, class_ids)))    #------> Set number of atribute
print('gdf with ids', gdf.head())

# split the truth data into training and test data sets and save each to a new shapefile
gdf_train = gdf.sample(frac=0.8)
gdf_test = gdf.drop(gdf_train.index)
print('gdf shape', gdf.shape, 'training shape', gdf_train.shape, 'test', gdf_test.shape)
gdf_train.to_file(dir+"\\train.shp")
gdf_test.to_file(dir+"\\test.shp")

