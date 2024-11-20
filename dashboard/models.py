from django.db import models
from accounts.models import User
from school.models import *

# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)



# notifications/templatetags/notification_tags.py
"""
from django import template
from ..models import Notification

register = template.Library()

@register.inclusion_tag('notifications/show_notifications.html', takes_context=True)
def show_notifications(context):
    request_user = context['request'].user
    notifications = Notification.objects.filter(user=request_user).order_by('-created_at')[:5]
    return {'notifications': notifications}

# notifications/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def mark_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications_list')

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})

# templates/base.html

<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
    <style>
        #notification-bar {
            position: fixed;
            top: 0;
            right: 0;
            width: 300px;
            background-color: #f1f1f1;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div id="notification-bar">
        {% show_notifications %}
    </div>
    {% block content %}
    {% endblock %}
</body>
</html>

# templates/notifications/show_notifications.html

{% for notification in notifications %}
    <div class="notification {% if not notification.is_read %}unread{% endif %}">
        {{ notification.message }}
        {% if not notification.is_read %}
            <a href="{% url 'mark_as_read' notification.id %}">Mark as read</a>
        {% endif %}
    </div>
{% empty %}
    <p>No new notifications.</p>
{% endfor %}

# templates/notifications/list.html

{% extends 'base.html' %}

{% block content %}
    <h1>Notifications</h1>
    {% for notification in notifications %}
        <div class="notification {% if not notification.is_read %}unread{% endif %}">
            {{ notification.message }}
            {% if not notification.is_read %}
                <a href="{% url 'mark_as_read' notification.id %}">Mark as read</a>
            {% endif %}
        </div>
    {% empty %}
        <p>No notifications.</p>
    {% endfor %}
{% endblock %}"""