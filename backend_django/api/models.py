# backend_django/api/models.py

from django.db import models 

# ----------------------------------------------------------------------
# 1. Budget OTB (Colección Original: budget_otb)
# ----------------------------------------------------------------------
class BudgetOTB(models.Model):
    # Asumimos que dept_id ahora es una clave foránea si se tiene una tabla de Departamentos/Tiendas
    # Pero por simplicidad, lo mantenemos como IntegerField si no hay tabla de Tiendas/Departamentos
    
    fiscal_year = models.IntegerField()
    fiscal_month = models.CharField(max_length=10)
    dept_id = models.IntegerField()
    allocated_receipts = models.FloatField() 
    
    # Campo para asegurar que no haya duplicados de mes/año/departamento
    class Meta:
        # unique_together es una buena práctica relacional
        unique_together = ('dept_id', 'fiscal_year', 'fiscal_month')

    def __str__(self):
        return f"OTB {self.dept_id} - {self.fiscal_month}/{self.fiscal_year}"


# ----------------------------------------------------------------------
# 2. Product Master (Colección Original: products_master)
# ----------------------------------------------------------------------
class ProductMaster(models.Model):
    style_id = models.CharField(max_length=50, unique=True)
    dept_id = models.IntegerField() # Mantener la relación con el departamento
    initial_cost = models.FloatField() 
    retail_price = models.FloatField()
    buy_qty_suggested_total = models.IntegerField(default=0) 

    def __str__(self):
        return self.style_id

# ----------------------------------------------------------------------
# 3. Stores Master (Colección Original: stores_master) <--- ¡NUEVO!
# ----------------------------------------------------------------------
class StoresMaster(models.Model):
    store_id = models.IntegerField(primary_key=True)
    store_name = models.CharField(max_length=100)
    region = models.CharField(max_length=50) # Ejemplo de campo
    
    def __str__(self):
        return self.store_name

# ----------------------------------------------------------------------
# 4. Transactions Sales (Colección Original: transactions_sales) <--- ¡NUEVO!
# ----------------------------------------------------------------------
class TransactionsSales(models.Model):
    # Relaciones: Usamos Foreign Keys para enlazar ventas a productos y tiendas
    
    # Enlace al producto vendido
    product = models.ForeignKey(ProductMaster, on_delete=models.CASCADE)
    # Enlace a la tienda donde ocurrió la venta
    store = models.ForeignKey(StoresMaster, on_delete=models.CASCADE)
    
    sale_date = models.DateField()
    sale_quantity = models.IntegerField()
    sale_price = models.FloatField()
    
    # Índice para acelerar consultas comunes
    class Meta:
        indexes = [
            models.Index(fields=['sale_date', 'store']),
        ]
        
    def __str__(self):
        return f"Venta {self.sale_quantity}x de {self.product.style_id}"