from django.contrib import admin
from .models import *
# Register your models here.


class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'vendor', 'order_date', 'status','is_deleted')  # Customize the fields displayed
    list_filter = ('status','is_deleted')# Enable filtering by the 'status' choice field
    search_fields = ('po_number', 'vendor__name')

admin.site.register(PurchaseOrder, PurchaseOrderAdmin)
admin.site.register(Vendor)