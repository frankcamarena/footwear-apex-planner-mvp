import os
import json
from datetime import datetime
from bson.objectid import ObjectId
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

# --- Configuración de la Conexión ---
# Utilizamos la variable de entorno MONGO_URI, que configurarás en Render.
MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    # Esto evita que el servidor se caiga si no se encuentra la variable en local
    print("WARNING: MONGO_URI no está configurada. Usando fallback.")
    MONGO_URI = "mongodb://localhost:27017/" # Reemplazar con una URL de fallback si es necesario

# Conexión al cliente de MongoDB Atlas
try:
    client = MongoClient(MONGO_URI)
    DB_NAME = "footwear" # <<-- IMPORTANTE: REEMPLAZA con el nombre de tu BD en Atlas
    db = client[DB_NAME]
    print(f"INFO: Conexión exitosa a la base de datos: {DB_NAME}")
except Exception as e:
    print(f"ERROR: Fallo en la conexión a MongoDB: {e}")
    # En un entorno de producción, podrías querer que la app no se inicie aquí

# --- Modelos de Pydantic (Validación de Datos) ---
# Usamos Pydantic para definir la estructura de datos que se espera
# y para serializar el JSON de salida.

class TransactionsSales(BaseModel):
    # La validación es CLAVE para los 150k+ registros
    transaction_id: Optional[str]
    store_id: Optional[str]
    sku_id: Optional[str]
    transaction_date: Optional[datetime]
    sales_units: Optional[int]
    sales_revenue: Optional[float]
    markdown_pct: Optional[float]
    # Otros campos que tengas en tu colección

class StoresMaster(BaseModel):
    store_id: Optional[str]
    store_name: Optional[str]
    # ... otros campos de StoresMaster

# --- Inicialización de FastAPI ---
app = FastAPI(
    title="Footwear Apex Planner MVP API (FastAPI + MongoDB)",
    description="API de alto rendimiento consumiendo datos de MongoDB Atlas."
)


# --- Middlewares y Configuración de CORS ---
# Necesario para que el frontend (React) pueda consumir esta API
from fastapi.middleware.cors import CORSMiddleware
origins = ["*"] # Para un MVP, permitimos cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Funciones Auxiliares ---
def serialize_mongo_doc(doc: dict) -> dict:
    """Convierte el _id de ObjectId a str y elimina campos innecesarios."""
    if doc.get('_id'):
        doc['_id'] = str(doc['_id'])
    return doc

# --- Endpoints de la API ---

@app.get("/", tags=["Health Check"])
def root():
    """Endpoint de estado del servicio."""
    return {"message": "API is running. Connected to MongoDB Atlas."}

@app.get("/api/sales", response_model=List[TransactionsSales], tags=["Data"])
async def get_sales_data(limit: int = 1000):
    """Obtiene datos de Transacciones de Ventas (limitado por defecto)."""
    try:
        sales_collection = db["transactions_sales"] # Reemplaza con el nombre real de tu colección
        
        # Consulta de PyMongo: Obtiene los documentos
        # IMPORTANTE: limitamos la salida para no sobrecargar el frontend, 
        # pero la consulta está sobre los 150k+ de registros en Atlas.
        data = list(sales_collection.find().limit(limit))
        
        # Serialización de los datos (de MongoDB a Python/JSON)
        serialized_data = [serialize_mongo_doc(doc) for doc in data]
        
        return serialized_data
    except Exception as e:
        print(f"ERROR al obtener datos de ventas: {e}")
        raise HTTPException(status_code=500, detail="Error al consultar datos de ventas.")

# Puedes añadir más endpoints aquí (ej: /api/stores, /api/products)