from django.shortcuts import render
from .models import Announcement
from .models import Notification
from accounts.models import Ticket

def announce(request):
    announcements = Announcement.objects.filter(is_active=True)
    return  {'announcements': announcements}

def tickets(request):
    
    tickets_count = Ticket.objects.all().exclude(status = 'Answered').count()
    return  {'tickets_count': tickets_count}




def notifications_context(request):
    if request.user.is_authenticated:
        base_qs = Notification.objects.filter(user=request.user)
        unread_count = base_qs.filter(is_read=False).count()
        notifications = base_qs.order_by('-created_at')[:10]
    else:
        notifications = []
        unread_count = 0

    return {
        'notifications': notifications,
        'unread_count': unread_count,
    }

 

