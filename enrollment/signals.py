from django.db.models.signals import pre_save, post_save
from accounts.models import User
from django.dispatch import receiver
from .models import *

@receiver(post_save, sender=U14Athlete)
def create_athlete_qr(sender, instance, created, **kwargs):
    if created:
        AthleteQR.objects.create(athlete=instance)