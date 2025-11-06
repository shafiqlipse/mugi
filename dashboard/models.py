from accounts.models import User
from django.utils.timezone import now
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from accounts.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    # Generic relation to link to *any* model (e.g. Request, Payment, Ticket)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=36, null=True, blank=True)  # ✅ allows UUIDs 
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.title} → {self.user.username}"




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
    
    
    





