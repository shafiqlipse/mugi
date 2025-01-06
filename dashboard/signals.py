from django.db.models.signals import post_save
from django.dispatch import receiver
from transfers.models import TransferRequest
from .models import Notification
from django.contrib.auth.models import User

@receiver(post_save, sender=TransferRequest)
def notify_ticket_update(sender, instance, created, **kwargs):
    if not created:  # Only trigger on updates
        # Define the recipients
        recipient1 = instance.requester  # Assuming the ticket owner is a recipient
        recipient2 = instance.owner  # Example second recipient
        
        # Create the notification
        notification = Notification.objects.create(
            sender=instance.approver,  # The user who updated the ticket
            verb='updated the ticket',
            target=f"Transfer #{instance.athlete}"
        )
        
        # Add recipients to the notification
        notification.recipients.add(recipient1, recipient2)
