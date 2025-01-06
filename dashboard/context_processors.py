from django.shortcuts import render
from .models import Announcement
from .models import Notification

def announce(request):
    announcements = Announcement.objects.filter(is_active=True)
    return  {'announcements': announcements}

def notifications(request):
    if request.user.is_authenticated and request.user.school:
        school = request.user.school
        notifications = Notification.objects.filter(recipients=school).order_by('-created_at')
        unread_count = notifications.filter(is_read=False).count()
        return {
            'notifications': notifications,
            'unread_notifications_count': unread_count,
        }
    return {'notifications': [], 'unread_notifications_count': 0}

