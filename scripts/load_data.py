#!/usr/bin/env python3
"""
Script para cargar datos de establecimientos desde JSON a PostgreSQL.
Este script se ejecuta una sola vez para migrar los datos.
"""

import os
import json
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

def load_environment():
    """Carga las variables de entorno desde el archivo .env"""
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL no está definida en el archivo .env")
    return database_url

def create_table_if_not_exists(cursor):
    """Crea la tabla establecimientos si no existe"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS establecimientos (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(255) NOT NULL,
        direccion VARCHAR(500),
        localidad VARCHAR(255),
        provincia VARCHAR(255)
    );
    """
    cursor.execute(create_table_query)
    print("✓ Tabla 'establecimientos' creada o verificada")

def load_json_data(json_file='tu_archivo_grande.json'):
    """
    Carga los datos desde el archivo JSON, extrayendo la lista de establecimientos.
    """
    print(f"📖 Leyendo datos desde {json_file}...")
    try:
        # 1. Cargar el JSON completo con la librería estándar
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 2. Seleccionar SOLAMENTE la lista de establecimientos
        establecimientos_lista = data['establecimientos']

        # 3. Crear el DataFrame a partir de esa lista específica
        df = pd.DataFrame(establecimientos_lista)
        
        # Verificar que las columnas necesarias existen
        required_columns = ['nombre', 'direccion', 'localidad', 'provincia']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Faltan las siguientes columnas en el JSON: {missing_columns}")
        
        # Limpiar datos: eliminar filas con nombre vacío y convertir NaN a None
        df = df.dropna(subset=['nombre'])
        df = df.fillna('')
        
        print(f"✓ Datos cargados: {len(df)} establecimientos encontrados")
        return df

    except FileNotFoundError:
        print(f"❌ Error: El archivo {json_file} no se encontró.")
        raise
    except KeyError:
        print(f"❌ Error: La clave 'establecimientos' no se encontró en el archivo JSON.")
        raise

def insert_data(cursor, df):
    """Inserta los datos en la base de datos"""
    print("📝 Insertando datos en la base de datos...")
    
    # Preparar datos para inserción
    data_to_insert = []
    for _, row in df.iterrows():
        data_to_insert.append((
            row['nombre'],
            row['direccion'],
            row['localidad'],
            row['provincia']
        ))
    
    # Insertar datos usando execute_values para mejor rendimiento
    insert_query = """
    INSERT INTO establecimientos (nombre, direccion, localidad, provincia)
    VALUES %s
    """
    
    execute_values(
        cursor,
        insert_query,
        data_to_insert,
        template=None,
        page_size=1000
    )
    
    print(f"✓ {len(data_to_insert)} establecimientos insertados")

def create_indexes(cursor):
    """Crea índices para optimizar las búsquedas"""
    print("🔍 Creando índices para optimizar búsquedas...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_establecimientos_provincia ON establecimientos (provincia);",
        "CREATE INDEX IF NOT EXISTS idx_establecimientos_nombre ON establecimientos (nombre);",
        "CREATE INDEX IF NOT EXISTS idx_establecimientos_direccion ON establecimientos (direccion);",
        "CREATE INDEX IF NOT EXISTS idx_establecimientos_nombre_ilike ON establecimientos USING gin (nombre gin_trgm_ops);",
        "CREATE INDEX IF NOT EXISTS idx_establecimientos_direccion_ilike ON establecimientos USING gin (direccion gin_trgm_ops);"
    ]
    
    for index_query in indexes:
        cursor.execute(index_query)
    
    print("✓ Índices creados para optimizar búsquedas")

def main():
    """Función principal del script"""
    try:
        print("🚀 Iniciando carga de datos de establecimientos...")
        
        # Cargar configuración
        database_url = load_environment()
        
        # Conectar a la base de datos
        print("🔌 Conectando a la base de datos...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Crear tabla
        create_table_if_not_exists(cursor)
        
        # Cargar datos del JSON
        df = load_json_data('tu_archivo_grande.json')
        
        # Limpiar datos existentes (opcional - comentar si quieres mantener datos previos)
        cursor.execute("DELETE FROM establecimientos;")
        print("✓ Datos existentes eliminados")
        
        # Insertar datos
        insert_data(cursor, df)
        
        # Crear índices
        create_indexes(cursor)
        
        # Confirmar cambios
        conn.commit()
        
        print("\n🎉 ¡Carga de datos completada exitosamente!")
        print(f"📊 Total de establecimientos cargados: {len(df)}")
        print("🔍 Índices creados para búsquedas rápidas")
        
    except Exception as e:
        print(f"❌ Error durante la carga de datos: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print("🔌 Conexión a base de datos cerrada")

if __name__ == "__main__":
    main()
