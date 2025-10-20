# transform_fixtures.py

import json
import os

# Mapeo de archivos JSON al nombre del modelo de Django
# (Nombre de la App.Nombre del Modelo)
MAPPING = {
    'synthetic_stores_master.json': 'api.storesmaster',
    'synthetic_products_master.json': 'api.productmaster',
    'synthetic_budget_otb.json': 'api.budgetotb',
    'synthetic_sales_data.json': 'api.transactionssales', 
}

# La carpeta donde se encuentran los archivos JSON
FIXTURES_DIR = 'backend_django/api/fixtures/'

def transform_json_to_fixture(filename, model_name):
    """Lee un JSON plano, lo transforma al formato de Fixture de Django y lo guarda."""
    input_path = os.path.join(FIXTURES_DIR, filename)
    
    print(f"--- Procesando: {filename} -> {model_name}")

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Archivo no encontrado en {input_path}")
        return

    transformed_data = []
    
    for index, item in enumerate(data):
        # 1. Definir la clave primaria (pk)
        # Usamos el campo "_id" si existe, o el índice si no.
        # Si "_id" es un string (como "JAN-2026-100"), lo usamos como PK de texto.
        # Si es un ID numérico, lo usamos como PK de número.
        
        # Asumiendo que el campo '_id' existe en todos tus modelos y es único:
        pk_value = item.pop('_id', index + 1)
        
        # 2. Construir el objeto fixture de Django
        fixture_item = {
            "model": model_name,
            "pk": pk_value, 
            "fields": item  # El resto de los campos van bajo 'fields'
        }
        transformed_data.append(fixture_item)

    # 3. Guardar el archivo transformado (sobrescribir el original)
    with open(input_path, 'w', encoding='utf-8') as f:
        json.dump(transformed_data, f, indent=2)
        
    print(f"✅ Transformación exitosa. {len(transformed_data)} objetos listos.")


if __name__ == "__main__":
    for filename, model_name in MAPPING.items():
        transform_json_to_fixture(filename, model_name)

    print("\n¡Todos los archivos JSON han sido convertidos al formato de Fixture de Django!")