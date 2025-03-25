"""
Download ephemeris from FTP.
NV 2022
"""
import os
from ftplib import FTP
import gnsscal
import  datetime
from  datetime import timedelta
host="lox.ucsd.edu"
"""Get the GPS week and DoY"""
def date(fecha):
    fecha=fecha.split("-")
    yy=int(fecha[0]);mm = int(fecha[1]);dd = int(fecha[2])
    fecha=datetime.date(yy,mm,dd)
    return fecha
print("input time interval to download ephemeris")
print("input star date (aaaa-mm-dd):",end="")
inicio=input()
inicio=date(inicio)
print("input ending date (aaaa-mm-dd):",end="")
fin=input()
fin=date(fin)
td=(fin-inicio).days
try:
    ftp = FTP(host)
    ftp.login()
    print("Conection sucessfull to a FTP")
    # open destination folder
    os.chdir(r"C:\\Users\\NicolasViasus\\Downloads")
    for d in range((fin - inicio).days + 1):
        fecha =inicio + timedelta(days=d)
        GPSwk=gnsscal.date2gpswd(fecha) #GPS Week
        dayGPSwk=(str(GPSwk[0])+str(GPSwk[1]))
        GPSwk=GPSwk[0]
        doy=gnsscal.date2doy(fecha) #GPS Day
        print("Date:"+str(fecha)+" GPS Day:" + str(doy)+"GPS week:"+str(GPSwk))
        ftp.cwd("/pub/products/" + str(GPSwk))
        #Varibale file name
        sp3 = "igr"+dayGPSwk+".sp3.Z"
        # open file binary mode
        sp3Open = open(sp3, 'wb')
        #download selected file
        ftp.retrbinary(f"RETR {sp3}",sp3Open.write)
        print("ephemeris "+sp3+" data downloaded")
except Exception as e:
    print(str(e))
print("ephemeris data downloaded!")
