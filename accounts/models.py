from django.db import models
from django.contrib.auth.models import AbstractUser
from django.apps import apps
import uuid 
# Create your models here.


class User(AbstractUser):
    is_school = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_zone = models.BooleanField(default=False)
    is_tech = models.BooleanField(default=False)
    is_accounts = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to="profile/", blank=True, null=True)
    school = models.ForeignKey(
        "school.School",
        related_name="users",
        on_delete=models.CASCADE,
        blank=True,  # Allows non-school users to leave this field empty
        null=True, db_index=True
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
    name = models.CharField(max_length=100, db_index=True)
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
    sport = models.ManyToManyField(Sport, verbose_name="Sport", blank=True)

    def __str__(self):
        return self.name

