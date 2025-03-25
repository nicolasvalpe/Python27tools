"""
script for generate reports from data

"""

import math
import statistics
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import os,glob,shutil


dir=r"C:\Users\NicolasViasus\Documents\Temporales_NV\JuanPabloII\IT Juan Pablo II\Juan pablo II\IT Parque Juan Pablo II"

GCP = dir+"\\7 Datos GNSS\\PXYZ.csv"
FT317=dir+"\\6 Reporte\\prueba.xlsx" #***CAMBIAR
print(GCP)
print(FT317)

Ex=dir+"\\1 Shp\\ex.csv"
dfGCP=pd.read_csv(GCP)
dfEx=pd.read_csv(Ex)
df0=pd.concat([dfGCP,dfEx],axis=1)
df0["Res_X"]=df0["Este"]-df0["X"]
df0["Res_Y"]=df0["Norte"]-df0["Y"]
df0["Res_Z"]=df0["Altura_Orto"]-df0["elev"]
print(df0)
Nptos=len(df0)
#get the mean
EmedioX=round((statistics.mean(df0["Res_X"])),3)
EmedioY=round((statistics.mean(df0["Res_Y"])),3)
EmedioZ=round((statistics.mean(df0["Res_Z"])),3)
#Get st_dev
sd_X=round((statistics.pstdev(df0["Res_X"])),3)
sd_Y=round((statistics.pstdev(df0["Res_Y"])),3)
sd_Z=round((statistics.pstdev(df0["Res_Z"])),3)
#Get RSME and acurazy
df0["X2"]=df0["Res_X"]**2
df0["Y2"]=df0["Res_Y"]**2
df0["Z2"]=df0["Res_Z"]**2
rsmeX=round(math.sqrt((sum(df0["X2"]))/Nptos),3)
rsmeY=round(math.sqrt((sum(df0["Y2"]))/Nptos),3)
rsmeZ=round(math.sqrt((sum(df0["Z2"]))/Nptos),3)
rsmeR=round((math.sqrt(rsmeX**2+rsmeY**2)),3)
PreH=round(rsmeR*1.7306,3)
PreZ=round((rsmeZ*1.96),3)
print("Precisión H: "+str(PreH)+" Precisión Z: "+str(PreZ))
#Export data
df0.to_csv()
