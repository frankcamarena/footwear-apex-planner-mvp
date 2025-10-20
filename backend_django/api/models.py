# backend_django/api/models.py
from django.db import models

# ======================================================================
# 1. StoresMaster (CORREGIDO)
# ======================================================================

class StoresMaster(models.Model):
    # PK: CharField para aceptar "STORE001" y "ECOMM"
    store_id = models.CharField(max_length=10, primary_key=True) 
    
    # Campos añadidos para coincidir con synthetic_stores_master.json
    store_location = models.CharField(max_length=100)
    store_cluster = models.CharField(max_length=10)
    store_type = models.CharField(max_length=10)
    max_option_capacity = models.IntegerField()
    opening_date = models.DateTimeField()
    
    # Nota: Se eliminaron store_name y region ya que no estaban en el JSON
    
    def __str__(self):
        return f'{self.store_id} - {self.store_location}'
    
    class Meta:
        verbose_name_plural = "Stores Master"


# ======================================================================
# 2. ProductMaster (CORREGIDO)
# ======================================================================

class ProductMaster(models.Model):
    # Clave primaria compuesta por STYLE-COLOR-SIZE (usada como PK en el fixture)
    pk_sku = models.CharField(max_length=50, primary_key=True, db_column='pk_sku')
    
    # Campos en el JSON:
    style_id = models.CharField(max_length=20)
    vendor_id = models.CharField(max_length=50)
    dept_id = models.IntegerField()
    gender = models.CharField(max_length=10)
    color_id = models.CharField(max_length=10)
    
    # DecimalField para el tamaño (e.g., 5.0, 10.5)
    size_us = models.DecimalField(max_digits=4, decimal_places=1) 
    
    # DECIMAL FIELD para Costo/Precio
    initial_cost = models.DecimalField(max_digits=10, decimal_places=2)
    # Nombre de campo corregido:
    initial_retail_price = models.DecimalField(max_digits=10, decimal_places=2) 
    
    core_rep_flag = models.CharField(max_length=10)
    repeat_new_flag = models.CharField(max_length=10)
    
    def __str__(self):
        return self.pk_sku
    
    class Meta:
        verbose_name_plural = "Products Master"


# ======================================================================
# 3. BudgetOTB (AJUSTADO)
# ======================================================================

class BudgetOTB(models.Model):
    # Clave primaria basada en el string (ej: JAN-2026-100)
    pk_otb = models.CharField(max_length=20, primary_key=True, db_column='pk_otb') 
    
    # Campos en el JSON:
    fiscal_year = models.IntegerField()
    fiscal_month = models.CharField(max_length=3)
    dept_id = models.IntegerField()
    allocated_receipts = models.DecimalField(max_digits=12, decimal_places=2)
    based_on_cogs_ly = models.DecimalField(max_digits=12, decimal_places=2)
    otb_status = models.CharField(max_length=10)
    
    def __str__(self):
        return self.pk_otb
    
    class Meta:
        verbose_name_plural = "Budget OTB"


# ======================================================================
# 4. TransactionsSales (CORREGIDO)
# ======================================================================

class TransactionsSales(models.Model):
    # PK: CharField para el ID de la transacción
    transaction_id = models.CharField(max_length=30, primary_key=True) 
    
    # FOREIGN KEYS
    # store_id debe apuntar a StoresMaster
    store = models.ForeignKey(StoresMaster, on_delete=models.DO_NOTHING) 
    # sku_id debe apuntar a ProductMaster
    product = models.ForeignKey(ProductMaster, on_delete=models.DO_NOTHING) 
    
    # Campos en el JSON:
    transaction_date = models.DateTimeField()
    quantity_sold = models.IntegerField()
    retail_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    initial_cost = models.DecimalField(max_digits=10, decimal_places=2)
    gm_dollars = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f'{self.transaction_id} @ {self.store.store_id}'
    
    class Meta:
        verbose_name_plural = "Transactions Sales"