from django.db import models
from accounts.models import *
import random
from django.core.validators import FileExtensionValidator
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from django.db.models.signals import post_delete
from django.dispatch import receiver


class School(models.Model):

    name = models.CharField(max_length=100)
    emis_number = models.CharField(max_length=100, unique=True)
    center_number = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=10,
        choices=[("Active", "Active"), ("Inactive", "Inactive")],
        default="Inactive",
    )
    badge = models.ImageField(
        upload_to="badge/",
        blank=True,
        null=True,
    )
    # Headteacher
    lname = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    fname = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
    )
    nin = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )
    created = models.DateField(
        auto_now_add=True,
        blank=True,
        null=True,
    )
    gender = models.CharField(
        max_length=1,
        choices=[("M", "Male"), ("F", "Female")],
        blank=True,
        null=True,
    )
    photo = models.ImageField(
        upload_to="badge/",
        blank=True,
        null=True,
    )

    # games teacher
    gfname = models.CharField(max_length=100, null=True, blank=True, default="")
    glname = models.CharField(max_length=100, null=True, blank=True, default="")
    gemail = models.EmailField(null=True, blank=True, default="", unique=True)
    gphone = models.CharField(max_length=15, null=True, blank=True, default="")
    gnin = models.CharField(
        max_length=20,
        default="",
        blank=True,
        null=True,
    )
    gdate_of_birth = models.DateField(
        blank=True,
        null=True,
    )
    ggender = models.CharField(
        max_length=1,
        choices=[("M", "Male"), ("F", "Female")],
        null=True,
        blank=True,
    )
    gphoto = models.ImageField(
        upload_to="badge/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class school_official(models.Model):
    added_by = models.ForeignKey(
        User,
        related_name="uploader",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    school = models.ForeignKey(
        School, related_name="officials", on_delete=models.CASCADE
    )
    fname = models.CharField(max_length=100, null=True, blank=True, default="")
    lname = models.CharField(max_length=100, null=True, blank=True, default="")
    email = models.EmailField(null=True, blank=True, default="")
    phone_number = models.CharField(max_length=15, null=True, blank=True, default="")
    nin = models.CharField(max_length=20, default="", unique=True)
    residence = models.CharField(max_length=20, default="", null=True)
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=1,
        choices=[("M", "Male"), ("F", "Female")],
        null=True,
        blank=True,
    )
    role = models.CharField(
        max_length=40,
        choices=[
            ("Coach", "Coach"),
            ("Teacher", "Teacher"),
            ("Assistant Games Teacher", "Assistant Games Teacher"),
            ("Assistant Head Teacher", "Assistant Head Teacher"),
            ("Nurse", "Nurse"),
            ("Doctor", "Doctor"),
            ("District Education Officer", "District Education Officer"),
            ("District Sports Officer", "District Sports Officer"),
        ],
        null=True,
        blank=True,
    )

    photo = models.ImageField(
        upload_to="badge/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.fname


class Classroom(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


from django.core.exceptions import ValidationError
import re


def validate_index_number(value):
    # Define the pattern for validation
    pattern = re.compile(r"^\d{6}/\d{3}/\d{4}$")
    if not pattern.match(value):
        raise ValidationError("Index number must be in the format YYYY/XXX/YYYY.")

    # Extract the year part from the index number
    parts = value.split("/")
    year = int(parts[2])
    if year < 2005:
        raise ValidationError("Year cannot exceed 2005.")


class Athlete(models.Model):
    school = models.ForeignKey(
        School, related_name="athletes", on_delete=models.CASCADE
    )

    athlete_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    fname = models.CharField(max_length=255)
    mname = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    lname = models.CharField(max_length=255)
    lin = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    index_number = models.CharField(
        max_length=255,
        unique=True,
        validators=[validate_index_number],
        null=True,
        blank=True,
    )
    uce_index_number = models.CharField(
        max_length=255,
        # unique=True,
        null=True,
        blank=True,
    )
    sport = models.ForeignKey(
        Sport,
        related_name="sport",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    date_of_birth = models.DateField()
    created = models.DateField(auto_now_add=True, null=True)
    gender = models.CharField(
        choices=[("Male", "male"), ("Female", "female")], max_length=10
    )
    classroom = models.ForeignKey(
        Classroom, related_name="classroom", on_delete=models.CASCADE
    )

    physic = models.CharField(
        max_length=25,
        choices=[("Normal", "Normal"), ("Special Needs", "Special Needs")],
        default="Normal",
        blank=True,
        null=True,
    )

    nationality = models.CharField(
        max_length=25,
        choices=[("National", "National"), ("Foreigner", "Foreigner")],
        default="National",
    )
    refugee = models.CharField(
        max_length=25,
        choices=[("Yes", "Yes"), ("No", "No")],
        blank=True,
        null=True,
    )
    sponsorship = models.CharField(
        max_length=25,
        choices=[
            ("School sponsored", "School sponsored"),
            ("Parent sponsored", "Parent sponsored"),
        ],
        blank=True,
        null=True,
    )

    photo = models.ImageField(upload_to="athlete_photos/")

    ple_certificate = models.FileField(
        upload_to="certificates/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        null=True,
        blank=True,
    )
    uce_certificate = models.FileField(
        upload_to="certificates/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        null=True,
        blank=True,
    )
    student_pass = models.FileField(
        upload_to="certificates/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        null=True,
        blank=True,
    )
    student_visa = models.FileField(
        upload_to="certificates/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        null=True,
        blank=True,
    )
    bursary = models.FileField(
        upload_to="certificates/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        null=True,
        blank=True,
    )
    student_pass_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    uneb_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    uneb_eq_results = models.FileField(
        upload_to="certificates/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        null=True,
        blank=True,
    )
    refugee_card = models.FileField(
        upload_to="certificates/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        null=True,
        blank=True,
    )

    Parent_fname = models.CharField(max_length=100)
    Parent_lname = models.CharField(max_length=100)
    parent_phone_number = models.CharField(max_length=15)
    parent_nin = models.CharField(max_length=20)
    address = models.CharField(max_length=20)
    relationship = models.CharField(
        max_length=15,
        choices=[("Father", "Father"), ("Mother", "Mother"), ("Other", "Other")],
    )
    # New field to track payment status
    added_by = models.ForeignKey(
        User,
        related_name="suploader",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    # New field to track payment status

    status = models.CharField(
        max_length=10,
        choices=[("New", "New"), ("Active", "Active"), ("Inactive", "Inactive")],
        null=True,
        blank=True,
        default="New",
    )

    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    def generate_qr_code(self):
        # Information you want encoded in the QR code
        qr_info = f"Name: {self.fname} {self.lname}\nSCHOOL: {self.school.name}\nLIN: {self.lin}\nGender: {self.gender}\nDate of Birth: {self.date_of_birth}\nSport: {self.sport.name}"

        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_info)
        qr.make(fit=True)

        # Create an image from the QR code
        qr_img = qr.make_image(fill="black", back_color="white").convert("RGB")
        qr_size = qr_img.size

        # Resize athlete's photo to fit inside the QR code (optional size adjustment)
        if self.photo:
            photo = Image.open(self.photo.path)  # Load the athlete's photo
            photo_size = (
                qr_size[0] // 4,
                qr_size[1] // 4,
            )  # Resize the photo to 1/4 of the QR code
            photo = photo.resize(photo_size)

            # Paste the athlete's photo at the center of the QR code
            qr_img.paste(
                photo,
                ((qr_size[0] - photo_size[0]) // 2, (qr_size[1] - photo_size[1]) // 2),
            )

        # Save the QR code to an in-memory file and then to the model field
        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        file_name = f"qr_{self.fname}_{self.lname}.png"
        self.qr_code.save(file_name, File(buffer), save=False)
        buffer.close()

    def save(self, *args, **kwargs):
        # Generate athlete_id if not already set
        if not self.athlete_id:
            self.athlete_id = self.generate_athlete_id()

        # Call the parent class save method first to ensure the instance exists in DB
        super(Athlete, self).save(*args, **kwargs)

        # Generate the QR code after saving the athlete instance
        self.generate_qr_code()

        # Save again to update the QR code field
        super(Athlete, self).save(*args, **kwargs)

    def generate_athlete_id(self):
        # Extract year from date_of_birth
        year = str(self.date_of_birth.year)[-2:]  # Get last two digits of the year

        # Set gender code (M for male, F for female)
        gender_code = "M" if self.gender == "Male" else "F"

        # Generate a random 4-digit number and ensure uniqueness
        while True:
            random_number = random.randint(1000, 9999)
            athlete_id = f"000{year}{gender_code}{random_number}"
            if not Athlete.objects.filter(athlete_id=athlete_id).exists():
                break

        return athlete_id

    def save(self, *args, **kwargs):
        # Generate athlete_id if not already set
        if not self.athlete_id:
            self.athlete_id = self.generate_athlete_id()

        super(Athlete, self).save(*args, **kwargs)


def clean(self):
    nationality = self.nationality
    refugee = self.refugee

    # Nationality checks
    if nationality == "National":
        if refugee:
            raise ValidationError("Refugee status cannot be set for national athletes.")
        if not self.index_number:
            raise ValidationError("Index number is required for nationals.")
        # No need for student_pass or refugee_card for nationals
        self.student_pass = None
        self.refugee_card = None
    elif nationality == "Foreigner":
        if self.index_number:
            raise ValidationError("Index number is not applicable for foreigners.")
        # Handle refugees and non-refugees separately
        if refugee == "Yes" and not self.refugee_card:
            raise ValidationError("Refugee card is required for refugees.")
        if refugee == "No" and not self.student_pass:
            raise ValidationError("Student pass is required for non-refugees.")

    return super().clean()
