import os
import json
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient

# IMPORTANTE: Necesitas esta línea para la serialización robusta de tipos BSON (ObjectId, ISODate)
from bson import json_util

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
    DB_NAME = "footwear" # Nombre de la BD confirmado
    db = client[DB_NAME]
    print(f"INFO: Conexión exitosa a la base de datos: {DB_NAME}")
except Exception as e:
    print(f"ERROR: Fallo en la conexión a MongoDB: {e}")
    # En un entorno de producción, podrías querer que la app no se inicie aquí

# --- Modelos de Pydantic (Aunque la respuesta final es forzada a JSON, es bueno tener la definición) ---
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

class BudgetOTB(BaseModel):
    # El _id de Mongo lo manejará la base de datos, pero el _id lógico ("JAN-2026-100") lo validamos aquí
    otb_id: str = Field(alias="_id", default=None) # Si usas el _id como identificador lógico, podemos mapearlo

    # Campos de Presupuesto
    fiscal_year: int
    fiscal_month: str
    dept_id: int
    allocated_receipts: float
    based_on_cogs_ly: float
    otb_status: str

    # Permite que la validación se realice incluso si los datos vienen con el campo "_id"
    model_config = {
        "extra": "ignore",
        "populate_by_name": True # Permite usar el alias como "_id"
    }

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

# --- Funciones Auxiliares (SERIALIZACIÓN ROBUSTA) ---
def serialize_mongo_doc(doc: dict) -> dict:
    """
    Convierte un documento BSON (con ObjectId, ISODate) en un diccionario
    JSON seguro. Esto resuelve el Internal Server Error.
    """
    # json_util.dumps convierte el documento a JSON string,
    # y json.loads lo convierte de nuevo a un dict estándar de Python.
    return json.loads(json_util.dumps(doc))

# --- Endpoints de la API ---

@app.get("/", tags=["Health Check"])
def root():
    """Endpoint de estado del servicio."""
    return {"message": "API is running. Connected to MongoDB Atlas."}

@app.get("/api/sales", tags=["Data"]) # <--- response_model ELIMINADO para evitar fallos de serialización
async def get_sales_data(limit: int = 1000):
    """Obtiene datos de Transacciones de Ventas (limitado por defecto)."""
    try:
        sales_collection = db["transactions_sales"] # Reemplaza con el nombre real de tu colección si no es correcto
        
        # Consulta de PyMongo: Obtiene los documentos
        # IMPORTANTE: limitamos la salida para no sobrecargar el frontend, 
        # pero la consulta está sobre los 150k+ de registros en Atlas.
        data = list(sales_collection.find().limit(limit))
        
        # Serialización de los datos (de MongoDB a Python/JSON)
        # Usamos la función robusta para manejar los tipos de BSON
        serialized_data = [serialize_mongo_doc(doc) for doc in data]
        
        return serialized_data # FastAPI devolverá el JSON
    except Exception as e:
        # Imprime el error completo en el log de Render
        print(f"ERROR CRÍTICO al obtener datos de ventas: {e}") 
        # Devuelve un mensaje de error más útil al cliente
        raise HTTPException(status_code=500, detail=f"Error al consultar datos de ventas. Revise el log de Render: {e}")
    
# --- AÑADE ESTO AL FINAL DEL ARCHIVO main.py ---

@app.get("/api/products", tags=["Data"])
async def get_products_data(limit: int = 1000):
    """Obtiene datos de la tabla maestra de Productos (limitado por defecto)."""
    try:
        # Reemplaza 'products_master' si tu colección se llama diferente en Atlas
        products_collection = db["products_master"] 
        
        # Consulta de PyMongo
        data = list(products_collection.find().limit(limit))
        
        # Serialización robusta
        serialized_data = [serialize_mongo_doc(doc) for doc in data]
        
        return serialized_data
    except Exception as e:
        print(f"ERROR CRÍTICO al obtener datos de productos: {e}")
        raise HTTPException(status_code=500, detail=f"Error al consultar datos de productos. Revise el log de Render: {e}")

# --- AÑADE ESTO PARA STORES (Tiendas) ---

@app.get("/api/stores", tags=["Data"])
async def get_stores_data(limit: int = 100):
    """Obtiene datos de la tabla maestra de Tiendas (limitado por defecto)."""
    try:
        # Reemplaza 'stores_master' si tu colección se llama diferente en Atlas
        stores_collection = db["stores_master"] 
        
        # Consulta de PyMongo
        data = list(stores_collection.find().limit(limit))
        
        # Serialización robusta
        serialized_data = [serialize_mongo_doc(doc) for doc in data]
        
        return serialized_data
    except Exception as e:
        print(f"ERROR CRÍTICO al obtener datos de tiendas: {e}")
        raise HTTPException(status_code=500, detail=f"Error al consultar datos de tiendas. Revise el log de Render: {e}")
    
# --- AÑADE ESTO AL FINAL DEL ARCHIVO main.py (después de get_stores_data) ---

@app.post("/api/otb_budget", tags=["Planning"])
async def post_otb_budget_data(budget_data: BudgetOTB):
    """
    Recibe un documento de presupuesto OTB, lo valida con Pydantic,
    CONSTRUYE el ID compuesto, y lo inserta, excluyendo campos no necesarios.
    """
    try:
        # 1. Convertir a diccionario. Excluimos campos si son None (null) o si tienen un alias 'id'/'otb_id'.
        # Nota: Usaremos model_dump() y luego limpiaremos el diccionario.
        budget_dict = budget_data.model_dump(exclude_none=True)
        
        # 2. CONSTRUIR el ID compuesto (ej: "JAN-2027-888")
        otb_id = f"{budget_data.fiscal_month}-{budget_data.fiscal_year}-{budget_data.dept_id}"
        
        # 3. Mapear el ID compuesto al campo '_id' de MongoDB
        budget_dict["_id"] = otb_id
        
        # 4. LIMPIEZA CRÍTICA: Eliminar cualquier campo que Pydantic haya incluido
        #    que no sea parte de tus datos, como el campo 'id' o 'otb_id' (que es None).
        if "otb_id" in budget_dict:
            budget_dict.pop("otb_id")
        if "id" in budget_dict: # En caso de que el campo se llame 'id'
            budget_dict.pop("id")
            
        # Seleccionar la colección de presupuesto
        budget_collection = db["budget_otb"]

        # Insertar el documento en MongoDB
        result = budget_collection.insert_one(budget_dict)
        
        if result.inserted_id:
            return {"status": "success", "message": "Budget OTB data inserted successfully", "id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="Database insertion failed.")

    except Exception as e:
        print(f"ERROR CRÍTICO en POST /api/otb_budget: {e}")
        if "duplicate key error" in str(e):
             raise HTTPException(status_code=409, detail="Error: El identificador de presupuesto (e.g., mes/año/dpto) ya existe.")

        raise HTTPException(status_code=500, detail=f"Error al procesar datos de presupuesto: {e}")
# --- Endpoint GET para Presupuesto OTB ---

@app.get("/api/otb_budget", tags=["Planning"])
async def get_otb_budget_data():
    """
    Obtiene todos los documentos de presupuesto OTB.
    """
    try:
        otb_collection = db["budget_otb"] 
        
        # Consulta de PyMongo: Obtiene todos los documentos (idealmente se filtraría, 
        # pero para el MVP tomamos todos los existentes)
        data = list(otb_collection.find())
        
        # Serialización robusta
        serialized_data = [serialize_mongo_doc(doc) for doc in data]
        
        return serialized_data
    except Exception as e:
        print(f"ERROR CRÍTICO al obtener datos de presupuesto OTB: {e}")
        raise HTTPException(status_code=500, detail=f"Error al consultar datos de presupuesto: {e}")

