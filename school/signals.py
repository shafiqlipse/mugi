from django.db.models.signals import pre_save, post_save
from accounts.models import User
from django.dispatch import receiver
from .models import *

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



@receiver(post_save, sender=school_official)
def manage_user_for_official(sender, instance, **kwargs):
    """Create or deactivate a User based on the official's status."""
    user = User.objects.filter(email=instance.email).first()  # Get the user if exists

    if instance.status == "Active":
        if not user:
            user = User.objects.create(
                email=instance.email,
                username=instance.email,  # Ensure uniqueness
                first_name=instance.fname,
                last_name=instance.lname,
                is_school=True,  # Set is_school=True
                is_active=True,  # Activate the user
            )
            user.set_password("Password@12345")  # Consider sending a password reset email
        else:
            user.is_active = True  # Reactivate if previously deactivated

        user.school = instance.school  # Assign school
        user.save(update_fields=["is_active", "school", "first_name", "last_name"])

    elif instance.status == "Inactive" and user:
        user.is_active = False  # Deactivate the user
        user.save(update_fields=["is_active"])