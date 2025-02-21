from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment

@receiver(post_save, sender=Payment)
def update_athlete_status_on_payment_completion(sender, instance, **kwargs):
    # Check if the payment status is COMPLETED
    if instance.status == "COMPLETED":
        # Update all related athletes to "ACTIVE"
        instance.athletes.update(status="ACTIVE")
