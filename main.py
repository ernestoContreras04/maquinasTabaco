#!/usr/bin/env python3
"""
API FastAPI para el buscador de establecimientos en España.
Proporciona endpoints para buscar máquinas de tabaco.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any

# Cargar variables de entorno
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(
    title="Buscador de Establecimientos España",
    description="API para buscar máquinas de tabaco en España",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_database_connection():
    """Obtiene una conexión a la base de datos PostgreSQL"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL no configurada")
    
    try:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        return conn
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a la base de datos: {str(e)}")

def build_search_query(search: Optional[str], provincia: Optional[str], skip: int, limit: int) -> tuple:
    """
    Construye la consulta SQL dinámica y segura para buscar establecimientos.
    
    Returns:
        tuple: (query_string, query_params)
    """
    base_query = """
    SELECT id, nombre, direccion, localidad, provincia
    FROM establecimientos
    WHERE 1=1
    """
    
    params = []
    param_count = 1
    
    # Agregar filtro de búsqueda por texto (solo en localidad)
    if search and search.strip():
        base_query += f" AND localidad ILIKE %s"
        search_param = f"%{search.strip()}%"
        params.append(search_param)
        param_count += 1
    
    # Agregar filtro por provincia
    if provincia and provincia.strip():
        base_query += f" AND provincia ILIKE %s"
        params.append(f"%{provincia.strip()}%")
        param_count += 1
    
    # Agregar ordenamiento y paginación
    base_query += " ORDER BY nombre ASC"
    base_query += f" LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    
    return base_query, params

@app.get("/")
async def root():
    """Endpoint raíz con información básica de la API"""
    return {
        "message": "Buscador de Establecimientos España API",
        "version": "1.0.0",
        "endpoints": {
            "establecimientos": "/api/establecimientos",
            "docs": "/docs"
        }
    }

@app.get("/api/establecimientos")
async def get_establecimientos(
    search: Optional[str] = Query(None, description="Búsqueda por localidad"),
    provincia: Optional[str] = Query(None, description="Filtrar por provincia"),
    skip: int = Query(0, ge=0, description="Número de resultados a omitir (paginación)"),
    limit: int = Query(25, ge=1, le=100, description="Número máximo de resultados a devolver")
):
    """
    Busca establecimientos con filtros opcionales y paginación.
    
    Args:
        search: Texto para buscar en localidad (case-insensitive)
        provincia: Provincia para filtrar (case-insensitive)
        skip: Número de resultados a omitir para paginación
        limit: Número máximo de resultados a devolver (máximo 100)
    
    Returns:
        Dict con los resultados y metadatos de paginación
    """
    conn = None
    cursor = None
    
    try:
        # Conectar a la base de datos
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Construir consulta
        query, params = build_search_query(search, provincia, skip, limit)
        
        # Ejecutar consulta
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Convertir resultados a lista de diccionarios
        establecimientos = [dict(row) for row in results]
        
        # Obtener el total de resultados (sin paginación) para metadatos
        count_query = """
        SELECT COUNT(*) as total
        FROM establecimientos
        WHERE 1=1
        """
        count_params = []
        
        if search and search.strip():
            count_query += " AND localidad ILIKE %s"
            search_param = f"%{search.strip()}%"
            count_params.append(search_param)
        
        if provincia and provincia.strip():
            count_query += " AND provincia ILIKE %s"
            count_params.append(f"%{provincia.strip()}%")
        
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()['total']
        
        # Calcular metadatos de paginación
        has_more = (skip + len(establecimientos)) < total_count
        next_skip = skip + limit if has_more else None
        
        return {
            "establecimientos": establecimientos,
            "pagination": {
                "total": total_count,
                "skip": skip,
                "limit": limit,
                "returned": len(establecimientos),
                "has_more": has_more,
                "next_skip": next_skip
            },
            "filters": {
                "search": search,
                "provincia": provincia
            }
        }
        
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la consulta a la base de datos: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.get("/api/provincias")
async def get_provincias():
    """
    Obtiene la lista de todas las provincias disponibles en la base de datos.
    Útil para poblar el select de provincias en el frontend.
    """
    conn = None
    cursor = None
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT DISTINCT provincia
        FROM establecimientos
        WHERE provincia IS NOT NULL AND provincia != ''
        ORDER BY provincia ASC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        provincias = [row['provincia'] for row in results]
        
        return {
            "provincias": provincias,
            "total": len(provincias)
        }
        
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la consulta a la base de datos: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.get("/health")
async def health_check():
    """Endpoint de salud para verificar que la API está funcionando"""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "message": "API funcionando correctamente"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
