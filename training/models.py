from django.db import models
from accounts.models import District

# Create your models here.


class Venue(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Discipline(models.Model):
    name = models.CharField(max_length=50)
    venue = models.ManyToManyField(Venue)

    def __str__(self):
        return self.name


class Trainee(models.Model):

    photo = models.ImageField(
        upload_to="trainee_photo/",
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    contact = models.CharField(max_length=50)
    place = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    entry_date = models.DateField(auto_now_add=True)
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female")],
    )
    designation = models.CharField(
        max_length=20,
        choices=[
            ("Student", "Student"),
            ("Primary Teacher", "Primary Teacher"),
            ("Secondary Teacher", "Secondary Teacher"),
            ("Other", "Other"),
        ],
    )
    photo = models.ImageField(upload_to="trainee_photos/")
    status = models.CharField(
        max_length=10,
        choices=[("Active", "Active"), ("Inactive", "Inactive")],
        default="Inactive",
    )
    course = models.CharField(
        max_length=40,
        choices=[
            ("Refereeing", "Refereeing"),
            ("Coaching", "Coaching"),
            ("Media", "Media"),
            ("Safeguarding", "Safeguarding"),
            ("First-Aid", "First-Aid"),
            ("Umpiring", "Umpiring"),
            ("Officiating", "Officiating"),
            (
                "SPORTS FACILITIES FACILITY MANAGEMENT",
                "SPORTS FACILITIES FACILITY MANAGEMENT",
            ),
        ],
    )
    residence_type = models.CharField(
        max_length=20,
        choices=[
            ("Residential", "Residential"),
            ("Non Residential", "Non Residential"),
        ],
    )
    is_paid = models.BooleanField(default=False)
    # is_trainee = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
