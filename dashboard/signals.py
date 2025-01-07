from django.db.models.signals import post_save
from django.dispatch import receiver
from transfers.models import TransferRequest
from .models import Notification
from django.contrib.auth.models import User

@receiver(post_save, sender=TransferRequest)
def notify_ticket_update(sender, instance, created, **kwargs):
    if not created:  # Only trigger on updates
        # Define the recipients
        recipient1 = instance.requester  # The user who requested the transfer
        recipient2 = instance.owner  # The owner of the transfer
        
        # Determine the status message
        status_message = {
            'accepted': 'has accepted the transfer',
            'approved': 'has approved the transfer',
            'rejected': 'has rejected the transfer',
        }.get(instance.status, 'updated the transfer')  # Default message if status is unknown
        
        # Create the notification
        notification = Notification.objects.create(
            sender=instance.approver,  # The user who approved/rejected the transfer
            verb=f"{status_message}",
            target=f"Transfer for athlete {instance.athlete.fname}"  # Assuming 'athlete' has a 'name' field
        )
        
        # Add recipients to the notification
        notification.recipients.add(recipient1, recipient2)

