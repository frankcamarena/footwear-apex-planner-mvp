# backend_django/api/models.py

from djongo import models

class BudgetOTB(models.Model):
    # Maps to the 'budget_otb' collection (Core of the MVP)
    fiscal_year = models.IntegerField()
    fiscal_month = models.CharField(max_length=10)
    dept_id = models.IntegerField()
    # The key budget number
    allocated_receipts = models.FloatField() 
    
    class Meta:
        db_table = 'budget_otb' 
        
class ProductMaster(models.Model):
    # Maps to the 'products_master' collection (For the Planning Matrix)
    style_id = models.CharField(max_length=50)
    dept_id = models.IntegerField()
    initial_cost = models.FloatField() # Crucial for OTB calculation
    retail_price = models.FloatField()
    
    # Placeholder for ML Suggestion (simulated initially)
    buy_qty_suggested_total = models.IntegerField(default=0) 

    class Meta:
        db_table = 'products_master'