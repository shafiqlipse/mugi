from django.db import models
from django.contrib.auth.models import AbstractUser
from django.apps import apps
import uuid 
# Create your models here.


class User(AbstractUser):
    is_school = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_tech = models.BooleanField(default=False)
    is_accounts = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to="profile/", blank=True, null=True)
    school = models.ForeignKey(
        "school.School",
        related_name="users",
        on_delete=models.CASCADE,
        blank=True,  # Allows non-school users to leave this field empty
        null=True,
    )

class Sport(models.Model):
    name = models.CharField(max_length=245)
    entries = models.IntegerField("Number of entries", default=30)

    class Meta:
        ordering = ["-name"]

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Zone(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Championship(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(
        max_length=10,
        choices=[("Active", "Active"), ("Inactive", "Inactive")],
        default="Inactive",
    )

    def __str__(self):
        return self.name


class Ticket(models.Model):
    title = models.CharField(max_length=100)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[("Open", "Open"), ("Picked up", "Picked up"), ("Answered", "Answered"), ("Closed", "Closed")],
        default="Open",
    )
    topic = models.CharField(
        max_length=20,
        choices=[("Registration", "Registration"), ("Athletes", "Athletes"), ("Officials", "Officials"), ("Enrollments", "Enrollments"), ("Payments", "Payments"), ("Championships", "Championships")],
        default="Open",
    )
    priority = models.CharField(
        max_length=20,
        choices=[("High", "High"), ("Medium", "Medium"), ("Low", "Low"), ("Urgent", "Urgent")],
        default="Medium",
    )
    ticket_id = models.CharField(max_length=12, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = f"#{uuid.uuid4().hex[:8].upper()}"  # Example: #1A2B3C4D
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title

class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='responses')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update ticket status based on the sender
        if self.responder.is_staff:
            self.ticket.status = 'Answered'
        else:
            self.ticket.status = 'School Response'
        self.ticket.save()
        
    def __str__(self):
        return f"Message from {self.responder.username} on {self.ticket.title}"
    def __str__(self):
        return self.ticket.title
    
    

from django.utils import timezone

class SystemStatus(models.Model):
    closure_start = models.DateTimeField(null=True, blank=True)
    closure_end = models.DateTimeField(null=True, blank=True)

    # @classmethod
    # def is_system_closed(cls):
    #     status = cls.objects.first()
    #     if status and status.closure_start and status.closure_end:
    #         now = timezone.now()
    #         return status.closure_start <= now <= status.closure_end
    #     return False
