# backend_django/api/urls.py

from django.urls import path
from .views import (
    OTBView, 
    ProductListView, 
    PlanningSaveView, 
    # Vistas que necesitas crear en views.py para las tablas faltantes:
    StoreListView,
    TransactionView, 
)  

urlpatterns = [
    # --- Endpoints de Planificación Principal ---
    
    # 1. Endpoint de Lectura para OTB (BudgetOTB)
    path('otb/', OTBView.as_view(), name='otb_budget'),
    
    # 2. Endpoint de Lectura para Productos (ProductMaster)
    path('products/', ProductListView.as_view(), name='product_list'), 
    
    # 3. Endpoint de Escritura/Procesamiento para la Planificación
    #    (Asumo que interactúa con BudgetOTB y ProductMaster)
    path('planning/', PlanningSaveView.as_view(), name='planning_save'), 

    # --- Endpoints de Datos Maestros y Transaccionales (NUEVOS) ---

    # 4. Endpoint para Tiendas (StoresMaster)
    #    Permite obtener la lista de tiendas.
    path('stores/', StoreListView.as_view(), name='store_list'),
    
    # 5. Endpoint para Transacciones de Ventas (TransactionsSales)
    #    Permite enviar o consultar datos de ventas históricas.
    path('transactions/', TransactionView.as_view(), name='transaction_data'), 
]