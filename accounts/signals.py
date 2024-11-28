from django.db.models.signals import post_save
from django.dispatch import receiver
from school.models import School, school_official
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

User = get_user_model()


@receiver(post_save, sender=School)
def create_school_officials_and_admin(sender, instance, created, **kwargs):
    if created:
        # Create headteacher official
        school_official.objects.create(
            school=instance,
            fname=instance.fname,
            lname=instance.lname,
            email=instance.email,
            phone_number=instance.phone_number,
            nin=instance.nin,
            date_of_birth=instance.date_of_birth,
            gender=instance.gender,
            role="Head Teacher",
            photo=instance.photo,
        )

        # Create games teacher official
        school_official.objects.create(
            school=instance,
            fname=instance.gfname,
            lname=instance.glname,
            email=instance.gemail,
            phone_number=instance.gphone,
            nin=instance.gnin,
            date_of_birth=instance.gdate_of_birth,
            gender=instance.ggender,
            role="Games Teacher",
            photo=instance.gphoto,
        )

        # Create the admin user for the headteacher
        admin_password = "Password@12345"  # Replace with secure password generation
        admin_user = User.objects.create(
            username=instance.email,
            email=instance.email,
            password=make_password(admin_password),
            is_school=True,
        )

        # Create the user for the games teacher
        games_teacher_password = (
            "Password@12345"  # Replace with secure password generation
        )
        games_teacher_user = User.objects.create(
            username=instance.gemail,
            email=instance.gemail,
            password=make_password(games_teacher_password),
            is_school=True,
        )

        # Set up email context and message details
        context = {
            "admin_username": instance.email,
            "admin_password": admin_password,
            "games_teacher_username": instance.gemail,
            "games_teacher_password": games_teacher_password,
        }

        # Render HTML email content
        html_message = render_to_string("accounts/email.html", context)
        plain_message = strip_tags(html_message)
        subject = "Your School Admin and Games Teacher Account Details"
        from_email = "noreply@usssaonline.com"
        recipient_list = [instance.email, instance.gemail]

        # Create and send the email
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=from_email,
            to=recipient_list,
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
