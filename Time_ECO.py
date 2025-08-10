
"""Script to calculate minimum distance and time from gnss data
NV2025"""
"""
print("(0) Minimun Distance (km), (1) Minimun time (min) ",end="")
cl=int(input())

if cl == 0:
    print("input the time of observation: ",end="")
    time = float(input())
    dsmin=((time-65)/3)+10 #kilometros
    print("minimun distance: "+str(round(dsmin,3))+" km")
else:
    print("input the distance between base: ",end="")
    Dist = float(input())
    timemin=65+(3*(Dist-10)) #minutes
    print("minimun time: "+str(round(timemin,1))+" min" )
"""

import pandas as pd
import math
from datetime import datetime

# ------------------------------
# Conversión de ECEF a WGS84
# ------------------------------
def ecef_to_wgs84(x, y, z):
    a = 6378137.0          # semieje mayor (m)
    e = 8.1819190842622e-2 # excentricidad

    b = math.sqrt(a**2 * (1 - e**2))
    ep = math.sqrt((a**2 - b**2) / b**2)
    p = math.sqrt(x**2 + y**2)
    th = math.atan2(a * z, b * p)

    lon = math.atan2(y, x)
    lat = math.atan2(z + ep**2 * b * math.sin(th)**3,
                     p - e**2 * a * math.cos(th)**3)
    N = a / math.sqrt(1 - e**2 * math.sin(lat)**2)
    alt = p / math.cos(lat) - N

    lon_deg = math.degrees(lon)
    lat_deg = math.degrees(lat)

    return lat_deg, lon_deg, alt

# ------------------------------
# Calcular tiempo de rastreo
# ------------------------------
def calcular_tiempo_rastreo_desde_header(ruta):
    inicio = None
    fin = None
    ecef_coords = None

    with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
        for linea in f:
            if "TIME OF FIRST OBS" in linea:
                datos = linea.split()
                inicio = datetime(
                    int(datos[0]), int(datos[1]), int(datos[2]),
                    int(datos[3]), int(datos[4]), int(float(datos[5])),
                    int((float(datos[5]) % 1) * 1_000_000)
                )
            elif "TIME OF LAST OBS" in linea:
                datos = linea.split()
                fin = datetime(
                    int(datos[0]), int(datos[1]), int(datos[2]),
                    int(datos[3]), int(datos[4]), int(float(datos[5])),
                    int((float(datos[5]) % 1) * 1_000_000)
                )
            elif "APPROX POSITION XYZ" in linea:
                coords = linea.split()[:3]
                ecef_coords = tuple(map(float, coords))

    if inicio and fin:
        duracion_horas = (fin - inicio).total_seconds() / 3600
    else:
        duracion_horas = float(input("Tiempo de rastreo en horas: "))

    if ecef_coords:
        lat, lon, alt = ecef_to_wgs84(*ecef_coords)
    else:
        lat, lon, alt = None, None, None

    return inicio, fin, duracion_horas, (lat, lon, alt)

# ------------------------------
# Distancia Haversine
# ------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

# ------------------------------
# Calcular distancias a estaciones
# ------------------------------
def estaciones(latitud, longitud, csv_path):
    try:
        df = pd.read_csv(r"C:\Nicolas\Cartografia\Red_Geodesica\RedGeoAc_RedNacional.csv")

        if "latitud" not in df.columns or "longitud" not in df.columns:
            raise ValueError("El CSV debe contener columnas 'latitud' y 'longitud'.")

        df["dist_km"] = df.apply(lambda row: haversine(latitud, longitud, row["latitud"], row["longitud"]), axis=1)
        df_sorted = df.sort_values(by="dist_km").reset_index(drop=True)

        return df_sorted
    except Exception as e:
        print(f"Error leyendo el CSV: {e}")
        return None

# ------------------------------
# Ejecución principal
# ------------------------------
if __name__ == "__main__":
    ruta = input("Ingrese la ruta del archivo RINEX: ").strip()
    inicio, fin, horas, wgs84_coords = calcular_tiempo_rastreo_desde_header(ruta)

    print("\n--- RESULTADOS ---")
    if inicio and fin:
        print(f"Tiempo de rastreo: {horas:.2f} horas")
        print(f"Inicio: {inicio}")
        print(f"Fin: {fin}")
    else:
        print(f"Tiempo de rastreo (manual): {horas:.2f} horas")
    # Mantener cálculo de dmin
    dmin = (((horas * 60) - 65) / 3) + 10
    print(f"Distancia mínima de rastreo: {dmin:.1f} kilómetros")


    if wgs84_coords[0] is not None:
        print(f"Latitud: {wgs84_coords[0]:.8f}°")
        print(f"Longitud: {wgs84_coords[1]:.8f}°")
        print(f"Altitud: {wgs84_coords[2]:.3f} m")

        # Calcular distancias a estaciones
        csv_path = r"C:\Nicolas\Cartografia\Red_Geodesica\RedGeoAc_RedNacional.csv"
        estaciones_ordenadas = estaciones(wgs84_coords[0], wgs84_coords[1], csv_path)

        if estaciones_ordenadas is not None:
            print("\nEstaciones Permanentes:")
            print(estaciones_ordenadas[["MRTNomencl","latitud", "longitud", "dist_km"]].head(10))

    else:
        print("No se encontraron coordenadas ECEF en el archivo.")


