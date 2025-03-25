import os
import csv
from exiftool import ExifToolHelper

def extract_metadata_to_csv(folder_path, output_csv):
    # Obtener la lista de todos los archivos JPEG en la carpeta
    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg')]

    # Lista para almacenar todos los metadatos
    all_metadata = []

    # Extraer metadatos de cada archivo
    with ExifToolHelper() as et:
        for file in files:
            metadata = et.get_metadata(file)
            for d in metadata:
                cleaned_data = {k.split(":")[-1]: v for k, v in d.items()}
                all_metadata.append(cleaned_data)

    # Obtener todas las claves posibles para asegurarse de que el CSV tiene todas las columnas necesarias
    all_keys = set()
    for data in all_metadata:
        all_keys.update(data.keys())
    all_keys = sorted(all_keys)  # Ordenar las claves para un CSV ordenado

    # Escribir los metadatos en el archivo CSV
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=all_keys)
        writer.writeheader()
        for data in all_metadata:
            writer.writerow(data)

# Ruta a la carpeta que contiene las fotos
folder_path = r"D:\MDA\Lomas de Turillas\DJI_202407020813_003_Crear-ruta-de-zona5"
# Ruta al archivo CSV de salida
output_csv = folder_path+"\metadata_img.csv"

# Llamar a la función para extraer los metadatos y exportarlos a CSV
extract_metadata_to_csv(folder_path, output_csv)

#Step 2 getting the UTC closet time 

import pandas as pd
import datetime

def find_pos_file(directory):
    """Encuentra el archivo .pos en el directorio dado."""
    for file_name in os.listdir(directory):
        if file_name.endswith('.pos'):
            return os.path.join(directory, file_name)
    raise FileNotFoundError("No se encontró un archivo .pos en el directorio especificado.")



def read_pos_file(pos_file_path):
    """Lee un archivo POS y devuelve un DataFrame con las trayectorias."""
    data = []
    with open(pos_file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('%'):
                continue  # Saltar líneas de encabezado
            parts = line.split()
            if len(parts) >= 14:  # Asumiendo que hay al menos 16 partes en los datos de trayectoria
                utc_time = parts[0] + ' ' + parts[1]
                # Convertir la cadena de tiempo a un objeto datetime
                utc_time = datetime.datetime.strptime(utc_time, "%Y/%m/%d %H:%M:%S.%f")
                data.append({
                    'utc_time': utc_time,
                    'lat': float(parts[2]),
                    'lon': float(parts[3]),
                    'height': float(parts[4]),
                    'sdn': float(parts[7]),
                    'sde': float(parts[8]),
                    'sdu': float(parts[9]),
                    # Agrega más columnas si es necesario
                })
    return pd.DataFrame(data)

def find_closest_time(photo_time, trajectory_times):
    """Encuentra la hora más cercana en la trayectoria para una hora de foto dada."""
    closest_time = min(trajectory_times, key=lambda x: abs(x - photo_time))
    return closest_time

def process_photos_and_trajectories(photos_csv_path, pos_file_path, output_csv_path):
    """Procesa las fotos y las trayectorias, y guarda las correlaciones en un archivo CSV."""
    # Leer los archivos
    photos_metadata = pd.read_csv(photos_csv_path)
    trajectory_data = read_pos_file(pos_file_path)

    # Asegurarse de que las columnas de tiempo estén en formato datetime
    photos_metadata['UTCAtExposure'] = pd.to_datetime(photos_metadata['UTCAtExposure'], format="%Y:%m:%d %H:%M:%S.%f")
    trajectory_data['utc_time'] = pd.to_datetime(trajectory_data['utc_time'])

    # Crear una lista para almacenar los resultados
    results = []

    # Iterar sobre cada fila en los metadatos de las fotos
    for index, row in photos_metadata.iterrows():
        photo_name = row['FileName']
        photo_time = row['UTCAtExposure']
        
        # Encontrar la fila correspondiente en los datos de trayectoria
        closest_time = find_closest_time(photo_time, trajectory_data['utc_time'])
        trajectory_row = trajectory_data.loc[trajectory_data['utc_time'] == closest_time]

        # Extraer los valores de la trayectoria más cercana
        lat = trajectory_row['lat'].values[0]
        lon = trajectory_row['lon'].values[0]
        height = trajectory_row['height'].values[0]
        sdn = trajectory_row['sdn'].values[0]
        sde = trajectory_row['sde'].values[0]
        sdu = trajectory_row['sdu'].values[0]

        # Guardar los resultados
        results.append({
            'photo_name': photo_name,
            'photo_time': photo_time,
            'closest_trajectory_time': closest_time,
            'lat': lat,
            'lon': lon,
            'height': height,
            'sdn': sdn,
            'sde': sde,
            'sdu': sdu
        })

    # Crear un DataFrame con los resultados
    results_df = pd.DataFrame(results)

    # Guardar los resultados en un nuevo archivo CSV
    results_df.to_csv(output_csv_path, index=False)
    print(f"Archivo '{output_csv_path}' generado con éxito.")

# Rutas a los archivos de entrada y salida
photos_csv_path = output_csv
pos_file_path = folder_path
output_csv_path = folder_path+"\Photos_PPK.csv"

# Procesar las fotos y trayectorias, y guardar el archivo de salida
process_photos_and_trajectories(photos_csv_path, pos_file_path, output_csv_path)
