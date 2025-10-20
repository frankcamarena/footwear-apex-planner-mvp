# backend_django/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework import status
# Importamos todos los modelos migrados a PostgreSQL
from .models import BudgetOTB, ProductMaster, StoresMaster, TransactionsSales


# ======================================================================
# SERIALIZERS (Convertidores de Modelo a JSON)
# ======================================================================

class ProductSerializer(ModelSerializer):
    """Serializador para el modelo ProductMaster."""
    class Meta:
        model = ProductMaster
        fields = ['style_id', 'dept_id', 'initial_cost', 'retail_price', 'buy_qty_suggested_total']

class StoreSerializer(ModelSerializer):
    """Serializador para el modelo StoresMaster."""
    class Meta:
        model = StoresMaster
        # Exponemos todos los campos de la tabla maestra de tiendas
        fields = ['store_id', 'store_name', 'region'] 

class TransactionSerializer(ModelSerializer):
    """Serializador para el modelo TransactionsSales."""
    class Meta:
        model = TransactionsSales
        # Nota: Por defecto, Django REST Framework convierte las Foreign Keys (product, store)
        # a IDs. Para incluir más detalles, se necesitaría usar Serializers anidados.
        fields = ['product', 'store', 'sale_date', 'sale_quantity', 'sale_price']


# ======================================================================
# 1. OTB VIEW
# ======================================================================

class OTBView(APIView):
    """
    Endpoint para recuperar el presupuesto OTB agregado.
    Ahora usa PostgreSQL.
    """
    def get(self, request, format=None):
        dept_id_str = request.query_params.get('dept')

        if not dept_id_str:
            return Response({"error": "The 'dept' parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            dept_id = int(dept_id_str)
        except ValueError:
            return Response({"error": "The 'dept' parameter must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Consulta PostgreSQL: No hay cambios en la sintaxis, ya que es estándar de Django ORM
        otb_data = BudgetOTB.objects.filter(
            dept_id=dept_id,
            fiscal_year=2026,
            fiscal_month__in=['JAN', 'FEB', 'MAR', 'APR']
        ).values('fiscal_month', 'allocated_receipts')
        
        total_otb_receipts = sum(item['allocated_receipts'] for item in otb_data)
        
        if not otb_data:
            return Response({"error": f"No OTB data found for department {dept_id} in 2026."}, status=status.HTTP_404_NOT_FOUND)

        response_data = {
            "dept_id": dept_id,
            "total_planned_otb": round(total_otb_receipts, 2),
            "monthly_breakdown": list(otb_data)
        }
        return Response(response_data)


# ======================================================================
# 2. PRODUCT LIST VIEW
# ======================================================================

class ProductListView(APIView):
    """
    Endpoint para obtener la lista de productos (estilos) para el Planner.
    Ahora usa PostgreSQL.
    """
    def get(self, request, format=None):
        dept_id_str = request.query_params.get('dept')

        if not dept_id_str:
            return Response({"error": "The 'dept' parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            dept_id = int(dept_id_str)
        except ValueError:
            return Response({"error": "The 'dept' parameter must be an integer."}, status=status.HTTP_400_BAD_REQUEST)
        
        product_list = ProductMaster.objects.filter(dept_id=dept_id)
        
        if not product_list:
            return Response({"error": f"No styles found for department {dept_id}."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product_list, many=True)
        
        response_data = {
            "dept_id": dept_id,
            "product_count": product_list.count(),
            "styles": serializer.data
        }
        return Response(response_data)

# ======================================================================
# 3. PLANNING SAVE VIEW
# ======================================================================

class PlanningSaveView(APIView):
    """
    Endpoint para recibir el JSON con las cantidades de compra planificadas.
    """
    def post(self, request, format=None):
        data = request.data
        
        if not isinstance(data, list) or not all('style_id' in item and 'planned_qty' in item for item in data):
            return Response(
                {"error": "Invalid data format. Expected a list of objects with 'style_id' and 'planned_qty'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lógica de guardado en PostgreSQL (Actualizar la tabla PlanningMatrix)
        # Aquí iría la lógica de escritura a la base de datos...
        
        saved_count = len(data)

        return Response(
            {
                "success": True,
                "message": f"Successfully processed {saved_count} planned styles.",
                "received_data_preview": data[:2]
            }, 
            status=status.HTTP_201_CREATED
        )

# ======================================================================
# 4. STORES MASTER VIEW (NUEVO)
# ======================================================================

class StoreListView(APIView):
    """
    Endpoint para recuperar la lista maestra de tiendas (StoresMaster).
    """
    def get(self, request, format=None):
        stores = StoresMaster.objects.all()
        serializer = StoreSerializer(stores, many=True)
        
        return Response({
            "store_count": stores.count(),
            "stores": serializer.data
        })

# ======================================================================
# 5. TRANSACTIONS SALES VIEW (NUEVO)
# ======================================================================

class TransactionView(APIView):
    """
    Endpoint para gestionar datos de ventas (TransactionsSales).
    GET: Consultar ventas (requiere filtros). POST: Cargar nuevas ventas.
    """
    def get(self, request, format=None):
        # Ejemplo de filtro, por ejemplo, por style_id
        product_id = request.query_params.get('style') 
        
        if product_id:
            transactions = TransactionsSales.objects.filter(product__style_id=product_id)
        else:
            # En un entorno real, no se devolverían todas las transacciones sin filtro
            transactions = TransactionsSales.objects.all()[:100] # Limitar a 100 para evitar sobrecarga
        
        serializer = TransactionSerializer(transactions, many=True)
        
        return Response({
            "transaction_count": transactions.count(),
            "transactions": serializer.data
        })

    def post(self, request, format=None):
        # Lógica para cargar un lote de transacciones de venta (Data Ingestion)
        serializer = TransactionSerializer(data=request.data, many=True)

        if serializer.is_valid():
            # Aquí iría la lógica para procesar las ventas y quizás agregarlas a un Data Warehouse
            # serializer.save() 
            
            return Response(
                {"success": f"Successfully received and validated {len(request.data)} sales records."}, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)