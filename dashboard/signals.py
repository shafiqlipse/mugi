# requests/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from school.models import AthleteEditRequest
from .utils import notify_user

@receiver(post_save, sender=AthleteEditRequest)
def edit_request_approved_notification(sender, instance, **kwargs):
    if instance.status == "APPROVED":
        notify_user(
            user=instance.requested_by,
            title="Request Approved",
            message=f"Your request #{instance.id} has been approved.",
            obj=instance,
            send_email=True
        )
