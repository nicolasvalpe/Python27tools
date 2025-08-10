import os, gzip, shutil
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
    print("Conexión exitosa al FTP")

    # Carpeta de destino
    destino_base = r"C:\Users\nvias\Downloads"
    os.makedirs(destino_base, exist_ok=True)

    for d in range((fin - inicio).days + 1):
        fecha = inicio + timedelta(days=d)
        year = fecha.year  # Año
        GPSwk, GPSday = gnsscal.date2gpswd(fecha)  # Semana GPS y día de la semana GPS
        doy = gnsscal.date2doy(fecha)  # Día juliano del año

        print(f"Fecha: {fecha}, GPS Week: {GPSwk}, GPS Day: {GPSday}, DOY: {doy}")

        # Crear carpeta con el nombre de la semana GPS si no existe
        carpeta_destino = os.path.join(destino_base, str(GPSwk))
        os.makedirs(carpeta_destino, exist_ok=True)

        # Navegar al directorio remoto correspondiente en el FTP
        ftp.cwd(f"/pub/products/{GPSwk}")

        # Nombre del archivo a descargar
        sp3_gz = f"IGS0DEMULT_{year}{doy:03d}1200_02D_05M_ORB.SP3.gz"
        print(f"Descargando: {sp3_gz}")

        # Ruta completa del archivo de salida
        archivo_gz = os.path.join(carpeta_destino, sp3_gz)

        # Descargar el archivo en modo binario
        with open(archivo_gz, 'wb') as sp3Open:
            ftp.retrbinary(f"RETR {sp3_gz}", sp3Open.write)

        print(f"Archivo {sp3_gz} descargado en {carpeta_destino}")

        # ---------- DESCOMPRESIÓN DEL ARCHIVO ----------
        archivo_descomprimido = archivo_gz.replace(".gz", "")  # Ruta sin .gz

        with gzip.open(archivo_gz, 'rb') as f_in:
            with open(archivo_descomprimido, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        print(f"Archivo descomprimido: {archivo_descomprimido}")

        # ---------- ELIMINAR EL ARCHIVO .gz ----------
        os.remove(archivo_gz)
        print(f"Archivo comprimido eliminado: {archivo_gz}")

    ftp.quit()
    print("Proceso completado.")

except Exception as e:
    print(f"Error: {str(e)}")
    