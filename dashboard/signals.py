from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from school.models import *


@receiver(post_save, sender=Athlete)
def notify_admin_new_athlete(sender, instance, created, **kwargs):
    if created:
        subject = "New Athlete Added"
        html_message = render_to_string(
            "emails/email_notification.html", {"athlete": instance}
        )
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        recipient_list = settings.ADMIN_EMAILS

        send_mail(
            subject,
            plain_message,
            from_email,
            recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
