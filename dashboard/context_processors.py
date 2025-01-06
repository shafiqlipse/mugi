from django.shortcuts import render
from .models import Announcement

def announce(request):
    announcements = Announcement.objects.filter(is_active=True)
    return  {'announcements': announcements}
