from django.db import models
from django.contrib.auth.models import User
# Create your models here.

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class CustomManager(models.Manager):
    def get_queryset(self):
        return super(__class__, self).get_queryset().filter(is_deleted=False)


class BaseAbstractStructure(models.Model):
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    cmobjects = CustomManager()

    class Meta:
        abstract = True



class Vendor(BaseAbstractStructure):
    """ Vendor Model """
    name = models.CharField(max_length=255, blank=True, null=True)
    contact_details = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    vendor_code = models.CharField(max_length=100, unique=True)
    on_time_delivery_rate = models.FloatField(default=0.0, blank=True, null=True)
    quality_rating_avg = models.FloatField(default=0.0, blank=True, null=True)
    average_response_time = models.FloatField(default=0.0, blank=True, null=True)
    fulfillment_rate = models.FloatField(default=0.0, blank=True, null=True)

    def __str__(self):
        return self.name


class PurchaseOrder(BaseAbstractStructure):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]

    po_number = models.CharField(max_length=100, unique=True)
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField()
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.po_number


class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey('Vendor', on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField(default=0.0, blank=True, null=True)
    quality_rating_avg = models.FloatField(default=0.0, blank=True, null=True)
    average_response_time = models.FloatField(default=0.0, blank=True, null=True)
    fulfillment_rate = models.FloatField(default=0.0, blank=True, null=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.date.strftime('%Y-%m-%d')}"