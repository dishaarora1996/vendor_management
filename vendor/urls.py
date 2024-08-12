
from django.urls import path, include
from .views import *

urlpatterns = [
    path('purchase_orders/', PurchaseOrderAPIView.as_view(), name='purchase_order'),
    path('purchase_orders/<int:po_id>/', PurchaseOrderAPIView.as_view(), name='purchase_order'),
    path('vendor/', VendorAPIView.as_view(), name='vendor'),
    path('vendor/<int:vendor_id>/', VendorAPIView.as_view(), name='vendor'),
]