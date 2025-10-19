from django.shortcuts import render

# backend_django/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import BudgetOTB
from rest_framework.serializers import ModelSerializer
from .models import ProductMaster # Asegúrate de que ProductMaster esté importado
from rest_framework import status # Importa para usar códigos de estado HTTP


class OTBView(APIView):
    """
    Endpoint to retrieve the total aggregated OTB budget for the planning window (JAN-APR 2026).
    Required Filter: dept_id
    """
    def get(self, request, format=None):
        dept_id_str = request.query_params.get('dept')

        if not dept_id_str:
            return Response({"error": "The 'dept' parameter is required."}, status=400)
        
        try:
            dept_id = int(dept_id_str)
        except ValueError:
            return Response({"error": "The 'dept' parameter must be an integer."}, status=400)
        
        # 1. Query MongoDB for the specific department and 4-month planning period.
        otb_data = BudgetOTB.objects.filter(
            dept_id=dept_id,
            fiscal_year=2026,
            fiscal_month__in=['JAN', 'FEB', 'MAR', 'APR']
        ).values('fiscal_month', 'allocated_receipts')
        
        # 2. Sum the receipts for the main dashboard total.
        total_otb_receipts = sum(item['allocated_receipts'] for item in otb_data)
        
        if not otb_data:
            return Response({"error": f"No OTB data found for department {dept_id} in 2026."}, status=404)

        # 3. Final API Response (JSON)
        response_data = {
            "dept_id": dept_id,
            "total_planned_otb": round(total_otb_receipts, 2),
            "monthly_breakdown": list(otb_data)
        }
        return Response(response_data)

# New Class

# Nuevo Serializador para la matriz de productos
class ProductSerializer(ModelSerializer):
    class Meta:
        model = ProductMaster
        # Exponemos todos los campos que el frontend necesita
        fields = ['style_id', 'dept_id', 'initial_cost', 'retail_price', 'buy_qty_suggested_total']

class ProductListView(APIView):
    """
    Endpoint para obtener la lista de productos (estilos) para el Planner.
    Incluye sugerencias simuladas (buy_qty_suggested_total).
    """
    def get(self, request, format=None):
        dept_id_str = request.query_params.get('dept')

        if not dept_id_str:
            return Response({"error": "The 'dept' parameter is required."}, status=400)
        
        try:
            dept_id = int(dept_id_str)
        except ValueError:
            return Response({"error": "The 'dept' parameter must be an integer."}, status=400)
        
        # Filtrar solo productos del departamento solicitado (e.g., Dept 100)
        product_list = ProductMaster.objects.filter(dept_id=dept_id)
        
        if not product_list:
            return Response({"error": f"No styles found for department {dept_id}."}, status=404)

        # Usar el serializador para convertir los objetos de Mongo a JSON
        serializer = ProductSerializer(product_list, many=True)
        
        response_data = {
            "dept_id": dept_id,
            "product_count": product_list.count(),
            "styles": serializer.data
        }
        return Response(response_data)

# NEW CLASS


class PlanningSaveView(APIView):
    """
    Endpoint para recibir el JSON con las cantidades de compra planificadas
    por el usuario desde la matriz de React y guardarlas en MongoDB.
    """
    def post(self, request, format=None):
        data = request.data
        
        # Validar la estructura básica de los datos (simulación de validación)
        if not isinstance(data, list) or not all('style_id' in item and 'planned_qty' in item for item in data):
            return Response(
                {"error": "Invalid data format. Expected a list of objects with 'style_id' and 'planned_qty'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 1. Procesamiento de datos y guardado simulado:
        # Aquí es donde normalmente se harían las validaciones OTB (si el total planificado 
        # supera el total presupuestado, etc.) y se actualizaría la base de datos.

        # SIMULACIÓN DE ACTUALIZACIÓN (Reemplaza la lógica de ProductMaster aquí en el futuro si es necesario)
        saved_count = len(data)

        # 2. Respuesta Final
        return Response(
            {
                "success": True,
                "message": f"Successfully saved {saved_count} planned styles to the database.",
                "received_data_preview": data[:2] # Muestra una vista previa de los primeros 2 items
            }, 
            status=status.HTTP_201_CREATED # Código 201: Recurso Creado/Actualizado
        )