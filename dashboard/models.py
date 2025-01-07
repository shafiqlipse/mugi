from accounts.models import User
from school.models import School
from django.db import models
from django.utils.timezone import now

class Notification(models.Model):
    recipients = models.ManyToManyField(School, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    verb = models.CharField(max_length=255)  # e.g., "updated your ticket"
    target = models.CharField(max_length=255, null=True, blank=True)  # e.g., "Ticket #123"
    created_at = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Notification: {self.verb}"



class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    banner = models.ImageField(
        upload_to="banners/"
    )
    link=models.URLField( max_length=255,
        blank=True,
        null=True,)
    def __str__(self):
        return self.title

    def is_visible(self):
        return self.is_active and (not self.end_date or self.end_date > now())