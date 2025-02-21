from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Payment

@receiver(pre_save, sender=Payment)
def update_athlete_status_on_payment_completion(sender, instance, **kwargs):
    if not instance.pk:
        # Payment is being created (initial status is PENDING), no need to update athletes
        return

    # Get the previous state of the payment from the database
    previous = Payment.objects.get(pk=instance.pk)

    # Check if status changed from PENDING to COMPLETED
    if previous.status == 'PENDING' and instance.status == 'COMPLETED':
        # Update all related athletes to ACTIVE
        instance.athletes.update(status='ACTIVE')
