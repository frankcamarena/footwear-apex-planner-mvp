# backend_django/api/urls.py
from django.urls import path
from .views import OTBView, ProductListView, PlanningSaveView  

urlpatterns = [
    # Endpoint de Lectura (OTB)
    path('otb/', OTBView.as_view(), name='otb_budget'),
    
    # Endpoint de Lectura (Productos)
    path('products/', ProductListView.as_view(), name='product_list'), 
    
    # Endpoint de Escritura (Planificación)
    path('planning/', PlanningSaveView.as_view(), name='planning_save'), 
]