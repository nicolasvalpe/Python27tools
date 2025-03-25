"""Script for generate report convert data GNSS"""

import pandas as pd

dir=r"D:\PROYECTOS 2023\RENE\prueba"
fadj=dir+"\\6 Reportes procesamiento\\adjusted.txt" #adjusted file
fpb=dir+"\\6 Reportes procesamiento\\processing_base.txt" #processing base files
fpr=dir+"\\6 Reportes procesamiento\\processing_rover.txt" #processing base files
fave=dir+"\\6 Reportes procesamiento\\average.txt" #processing base files

#Get table data processing base  
pb=pd.read_table(fpb,encoding="utf-16"); df_pb=pd.DataFrame(pb.iloc[:,[1,2,4,6,7,8,9,10,11,12,13,14,19,20,21,32,33,34,38,39,40,41]])
#replace name of colums
df_pb.columns=["Point Id", "Station", "Solution Type", "Satellite System", "Frequency", "Occupation Mode", "Start Time", "End Time", "Duration", "Antenna Height (m)", "Antenna Name", "Ephemeris Type", "X", "Y", "Z", "SDx", "SDy", "SDz", "GDOP", "PDOP", "HDOP", "VDOP"]

#Get table data processing rover  
pr=pd.read_table(fpr,encoding="utf-16"); df_pr=pd.DataFrame(pr.iloc[:,[1,2,4,6,7,8,9,10,11,12,13,14,19,20,21,32,33,34,38,39,40,41]])
#replace name of colums
df_pr.columns=["Point Id", "Station", "Solution Type", "Satellite System", "Frequency", "Occupation Mode", "Start Time", "End Time", "Duration", "Antenna Height (m)", "Antenna Name", "Ephemeris Type", "X", "Y", "Z", "SDx", "SDy", "SDz", "GDOP", "PDOP", "HDOP", "VDOP"]

#get Sd table for adjusted points 
adj=pd.read_table(fadj,encoding="utf-16")
df_sd=pd.DataFrame(adj[["Point Id","Latitude [°]","Longitude [°]","Ellip. Height [m]","SD Easting [m]","SD Northing [m]","SD Ortho. Height [m]"]])
df_pb.X.astype("float")
print(df_pb["X"].dtype)

