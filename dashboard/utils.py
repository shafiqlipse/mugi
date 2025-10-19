# notifications/utils.py
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from .models import Notification

def notify_user(user, title, message, obj=None, send_email=False):
    """
    Create a system notification and optionally send an email.
    """
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        content_type=ContentType.objects.get_for_model(obj) if obj else None,
        object_id=obj.id if obj else None,
    )

    if send_email:
        send_mail(
            subject=title,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

    return notification
