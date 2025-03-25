from scipy.io import loadmat
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np
import os,glob

print("input data for convertr mat files:",end=" ")
DIR=input()

#iterate folder
for files in os.listdir(DIR):
    if files.endswith(".mat"): #Selecting Mat files
        print(files)
        namedata=files.replace(".mat","")
        file=DIR+"\\"+files
        """Load Mat file"""
        data=loadmat(file) #data is a Dict
        """Selecting data from Dict"""
        #config the depth sensor
        setup=data["Setup"]
        sensorDepth=setup["sensorDepth"]
        sensorDepth=sensorDepth[0,0]
        if sensorDepth==0.15:
            value=0
        else:
            value=sensorDepth
        value=float(value)
        print(value)
        #Create Dic
        System=data["System"]; Summary=data["Summary"]; GPS=data["GPS"]
        #Create Ndarray
        step=System["Step"]; sample=System["Sample"]; long=GPS["Longitude"]; lat=GPS["Latitude"]; depth=Summary["Depth"]
        #Select data from array
        step1=step[0,0]; sample1=sample[0,0]; long1=(long[0,0]); lat1=(lat[0,0]); Depth1=(depth[0,0])
        #Create dataframe and concatenate
        dfstep=pd.DataFrame(step1);dfsample=pd.DataFrame(sample1);dfX=pd.DataFrame(long1);dfY=pd.DataFrame(lat1);dfDepth=pd.DataFrame(Depth1)
        dfFinal=pd.concat([dfstep,dfsample,dfY,dfX,dfDepth],axis=1)
        dfFinal.columns=["Step","Sample","Latitud","Longitud","Depth"]
        dfFinal["Depth"]=dfFinal["Depth"]-value
        dfFinal["Transecto"]=namedata
        dfFinal["Transecto"]=dfFinal["Transecto"].str.replace('r','')
        dfFinal.to_csv((DIR+"\\"+namedata+".csv"), index=False)

all_data=glob.glob(os.path.join(DIR,"*r.csv"))
dfone=(pd.read_csv(f,sep=",") for f in all_data)
dfconcat=pd.concat(dfone,ignore_index=False) #Dataframe merge
dfconcat['Transecto_ID'] = dfconcat.groupby('Transecto').ngroup() + 1
dfconcat.to_csv(DIR+"\\compilado.csv") #Export to file csv

"""Convert to shapefile"""
points=dfconcat.apply(lambda point:Point(point. Longitud, point.Latitud),axis=1) #Set geometry
gdf=gpd.GeoDataFrame(dfconcat,geometry=points) #geodataframe
gdf.crs = "EPSG:4326"
gdf.to_file(DIR+"\\Batimetria.shp")
#Process: Project data to CTM12
CTM12 = "+proj=tmerc +lat_0=4 +lon_0=-73 +k=0.9992 +x_0=5000000 +y_0=2000000 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
gdf=gdf.to_crs(CTM12)
print("Shapefile generated sucessfull! ")
