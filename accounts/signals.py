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
        # Create headteacher
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

        # Create games teacher
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

        # Create school admin credentials
        school_admin_email = instance.email
        school_games_email = instance.gemail
        school_admin_username = instance.email
        school_admin_password = "123Pass"  # Replace with secure password generation

        # Create a school admin user and associate it with the school
        hashed_password = make_password(school_admin_password)
        school_admin_user = User.objects.create(
            username=school_admin_username,
            email=school_admin_email,
            password=hashed_password,
            is_school=True,
        )
        instance.user = school_admin_user

        instance.save()

        # Send email to the admin

        # Existing context
        context = {
            "school_admin_username": school_admin_username,
            "school_admin_password": school_admin_password,
        }

        # Load the HTML content from a template
        html_message = render_to_string("accounts/email.html", context)

        # Plain text alternative for email clients that don't support HTML
        plain_message = strip_tags(html_message)

        # Email subject and sender details
        subject = "Your School Admin Account Details"
        from_email = "noreply@usssaonline.com"
        recipient_list = [school_admin_user.email, school_games_email]

        # Set up the EmailMultiAlternatives object
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,  # Plain text version
            from_email=from_email,
            to=recipient_list,
        )

        # Attach the HTML content
        email.attach_alternative(html_message, "text/html")

        # Send the email
        email.send()
