from django.db.models import Count, F, ExpressionWrapper, fields, Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import PurchaseOrder


@receiver(post_save, sender=PurchaseOrder)
def calculate_metrics(sender, instance, created, **kwargs):

    if instance.status == 'completed':

        # Only calculate if the PO status is completed
        update_on_time_delivery_rate(instance)

        # Calculate the average quality rating for completed POs of the same vendor
        if instance.quality_rating is not None:
            update_quality_rating(instance)

    if instance.acknowledgment_date:
        update_average_response_time(instance)


def update_average_response_time(instance):
        # Filter all POs of the vendor that have acknowledgment_date set
        acknowledged_pos = PurchaseOrder.objects.filter(
            vendor=instance.vendor,
            acknowledgment_date__isnull=False
        ).annotate(
            response_time=ExpressionWrapper(
                F('acknowledgment_date') - F('issue_date'),
                output_field=fields.DurationField()
            )
        )

        # Calculate the average response time
        if acknowledged_pos.exists():
            avg_response_time = acknowledged_pos.aggregate(
                avg_response=Avg('response_time')
            )['avg_response']
            instance.vendor.average_response_time = avg_response_time.total_seconds()  # Convert to seconds
            instance.vendor.save()



def update_quality_rating(instance):
    completed_pos = PurchaseOrder.objects.filter(
        vendor=instance.vendor,
        status='completed',
        quality_rating__isnull=False
    )

    if completed_pos.exists():
        avg_rating = completed_pos.aggregate(avg_rating=Avg('quality_rating'))['avg_rating']
        instance.vendor.quality_rating_avg = avg_rating
        instance.vendor.save()

def update_on_time_delivery_rate(instance):
    # Set the actual delivery date if not already set
    if not instance.actual_delivery_date:
        instance.actual_delivery_date = timezone.now()
        instance.save()

    # Calculate on-time delivery rate
    total_completed = PurchaseOrder.objects.filter(vendor=instance.vendor, status='completed').count()
    on_time_deliveries = PurchaseOrder.objects.filter(
        vendor=instance.vendor,
        status='completed',
        actual_delivery_date__lte=F('delivery_date')
    ).count()
    on_time_rate = (on_time_deliveries / total_completed) * 100 if total_completed > 0 else 0.0

    # Update the vendor's on-time delivery rate
    instance.vendor.on_time_delivery_rate = on_time_rate
    instance.vendor.save()


