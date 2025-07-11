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

    name = models.CharField(max_length=100, db_index=True)
    emis_number = models.CharField(max_length=100, unique=True)
    center_number = models.CharField(max_length=100, db_index=True)
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
        School, related_name="officials", on_delete=models.CASCADE, db_index=True
    )
    fname = models.CharField(max_length=100, null=True, blank=True, default="")
    lname = models.CharField(max_length=100, null=True, blank=True, default="")
    email = models.EmailField(null=True, blank=True, default="", db_index=True)
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
    status = models.CharField(
        max_length=10,
        choices=[("Active", "Active"), ("Inactive", "Inactive")],
        default='New',
        null=True,
        blank=True,
    )
    role = models.CharField(
        max_length=40,
        choices=[
            ("Coach", "Coach"),
            ("HeadTeacher", "HeadTeacher"),
            ("GamesTeacher", "GamesTeacher"),
            ("Teacher", "Teacher"),
            ("Assistant Games Teacher", "Assistant Games Teacher"),
            ("Assistant Head Teacher", "Assistant Head Teacher"),
            ("Nurse", "Nurse"),
            ("Doctor", "Doctor"),
           
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
        raise ValidationError("Index number must be in the format AAAAAA/XXX/YYYY.")

    # Extract the year part from the index number
    parts = value.split("/")
    year = int(parts[2])
    if year < 2005:
        raise ValidationError("Year cannot be below 2005.")


class Athlete(models.Model):
    school = models.ForeignKey(
        School, related_name="athletes", on_delete=models.CASCADE, db_index=True
    )

    # athlete_id = models.CharField(max_length=255,  null=True, blank=True)
    fname = models.CharField(max_length=255, db_index=True)
    mname = models.CharField(max_length=255, null=True, blank=True)
    lname = models.CharField(max_length=255)
    lin = models.CharField(max_length=255, unique=True, null=True, blank=True)
    index_number = models.CharField(
        max_length=255, unique=True, validators=[validate_index_number], null=True, blank=True, db_index=True
    )
    uce_index_number = models.CharField(max_length=255, null=True, blank=True)
    sport = models.ForeignKey(Sport, related_name="sport", on_delete=models.CASCADE, null=True, blank=True)
    date_of_birth = models.DateField(db_index=True)
    created = models.DateField(auto_now_add=True, null=True)
    gender = models.CharField(choices=[("Male", "male"), ("Female", "female")], max_length=10)
    classroom = models.ForeignKey(Classroom, related_name="classroom", on_delete=models.CASCADE)
    # physic = models.CharField(
    #     max_length=25, choices=[("Normal", "Normal"), ("Special Needs", "Special Needs")],
    #     default="Normal", blank=True, null=True
    # )
    # nationality = models.CharField(
    #     max_length=25, choices=[("National", "National"), ("International", "International"), ("Foreigner", "Foreigner")],
    #     default="National"
    # )
    # refugee = models.CharField(max_length=25, choices=[("Yes", "Yes"), ("No", "No")], blank=True, null=True)
    sponsorship = models.CharField(
        max_length=25, choices=[("School sponsored", "School sponsored"), ("Parent sponsored", "Parent sponsored")],
        blank=True, null=True
    )
    photo = models.ImageField(upload_to="athlete_photos/")
    ple_certificate = models.FileField(upload_to="certificates/", validators=[FileExtensionValidator(allowed_extensions=["pdf"])], null=True, blank=True)
    uce_certificate = models.FileField(upload_to="certificates/", validators=[FileExtensionValidator(allowed_extensions=["pdf"])], null=True, blank=True)
    # student_pass = models.FileField(upload_to="certificates/", validators=[FileExtensionValidator(allowed_extensions=["pdf"])], null=True, blank=True)
    # student_visa = models.FileField(upload_to="certificates/", validators=[FileExtensionValidator(allowed_extensions=["pdf"])], null=True, blank=True)
    # bursary = models.FileField(upload_to="certificates/", validators=[FileExtensionValidator(allowed_extensions=["pdf"])], null=True, blank=True)
    # student_pass_code = models.CharField(max_length=255, null=True, blank=True)
    # uneb_code = models.CharField(max_length=255, null=True, blank=True)
    # uneb_eq_results = models.FileField(upload_to="certificates/", validators=[FileExtensionValidator(allowed_extensions=["pdf"])], null=True, blank=True)
    # refugee_card = models.FileField(upload_to="certificates/", validators=[FileExtensionValidator(allowed_extensions=["pdf"])], null=True, blank=True)
    Parent_fname = models.CharField(max_length=100)
    Parent_lname = models.CharField(max_length=100)
    parent_phone_number = models.CharField(max_length=15)
    parent_nin = models.CharField(max_length=20)
    address = models.CharField(max_length=20)
    relationship = models.CharField(
        max_length=15, choices=[("Father", "Father"), ("Mother", "Mother"), ("Other", "Other")]
    )

    added_by = models.ForeignKey(User, related_name="suploader", on_delete=models.CASCADE, null=True, blank=True)

    status = models.CharField(
        max_length=10, choices=[
            ("NEW", "NEW"), ("ACTIVE", "ACTIVE"), ("INACTIVE", "INACTIVE"), ("COMPLETED", "COMPLETED")
        ],
        null=True, blank=True, default="NEW", db_index=True
    )

    def __str__(self):
        return f"{self.fname} {self.lname}"


    # def save(self, *args, **kwargs):

    #     super(Athlete, self).save(*args, **kwargs)
        
# def clean(self):
#     nationality = self.nationality
#     refugee = self.refugee

#     # Nationality checks
#     if nationality == "National":
#         if refugee:
#             raise ValidationError("Refugee status cannot be set for national athletes.")
#         if not self.index_number:
#             raise ValidationError("Index number is required for nationals.")
#         # No need for student_pass or refugee_card for nationals
#         self.student_pass = None
#         self.refugee_card = None
#     # Nationality checks
#     elif nationality == "International":
#         if refugee:
#             raise ValidationError("Refugee status cannot be set for national athletes.")
#         if not self.lin:
#             raise ValidationError("lin is required for nationals.")
#         # No need for student_pass or refugee_card for nationals
#         self.student_pass = None
#         self.refugee_card = None
#         self.index_number = None
#         self.student_pass_code = None
#         self.student_visa = None
        
#     elif nationality == "Foreigner":
#         if self.index_number:
#             raise ValidationError("Index number is not applicable for foreigners.")
#         # Handle refugees and non-refugees separately
#         if refugee == "Yes" and not self.refugee_card:
#             raise ValidationError("Refugee card is required for refugees.")
#         if refugee == "No" and not self.student_pass:
#             raise ValidationError("Student pass is required for non-refugees.")

#     return super().clean()


class Screening(models.Model):

    athlete = models.ForeignKey(
        Athlete, related_name="athlete", on_delete=models.CASCADE, db_index=True
    )
    screener = models.ForeignKey(
        User, related_name="screener", on_delete=models.CASCADE
    )
    status = models.CharField(
        choices=[
            ("Impersonation", "Impersonation"),
            ("Overage", "Overage"),
            ("Underage", "Underage"),
            ("Misconduct", "Misconduct"),
            ("No UCE Results", "No UCE Results"),
            ("Two Passports", "Two Passports"),
            ("Unclear Identity", "Unclear Identity"),
            ("Other", "Other"),
        ],
        max_length=20,
    )
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.athlete


import random
import string
   
class Payment(models.Model):

        transaction_id = models.CharField(max_length=100,null=True, blank=True)
        amount = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
     
        phone_number = models.CharField(max_length=15)
        status = models.CharField(
        max_length=20, 
        choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], 
        default='PENDING'
    )
  
        created_at = models.DateTimeField(auto_now_add=True)
        school = models.ForeignKey(School, on_delete=models.CASCADE, db_index=True)
        athletes = models.ManyToManyField(Athlete, related_name='payments', db_index=True)
        def __str__(self):
            return f"{self.transaction_id} - {self.amount} {self.school}"