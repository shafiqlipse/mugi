from django.db.models.signals import pre_save
from django.dispatch import receiver
from accounts.models import User  # Adjust this if using a custom user model
from .models import Zonalchair

@receiver(pre_save, sender=Zonalchair)
def create_user_for_active_chair(sender, instance, **kwargs):
    if instance.id:  # Ensure it's an update, not a new instance
        previous = Zonalchair.objects.get(id=instance.id)
        if previous.status != "active" and instance.status == "active" and not instance.user:
            # Create a user
            
            base_username = instance.email.split('@')[0]

            # Generate a default password
            default_password = "Zonals@12345"
            
            user = User.objects.create_user(
                username=instance.email,  # Ensure unique username logic
                email=instance.email,
                password= default_password, 
                is_zone = True# You might want to generate a secure password
            )
            instance.user = user  # Assign created user to the Zonalchair instance
