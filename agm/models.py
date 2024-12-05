from django.db import models
from accounts.models import District, Region, Zone

# Create your models here.


class Delegates(models.Model):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    photo = models.ImageField(
        upload_to="agm_photo/",
    )

    district = models.ForeignKey(
        District,
        related_name="district",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    region = models.ForeignKey(
        Region,
        related_name="agm_region",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
    )
    zone = models.ForeignKey(Zone, related_name="agm_zone", on_delete=models.CASCADE)

    contact = models.CharField(max_length=15)
    school = models.CharField(max_length=125)

    gender = models.CharField(
        max_length=14,
        choices=[("Male", "Male"), ("Female", "Female")],
    )

    position = models.CharField(
        max_length=44,
        choices=[
            ("President ", "President "),
            ("President Emeritus ", "President Emeritus "),
            ("Vice President 1", "Vice President 1"),
            ("Vice President 2", "Vice President 2"),
            ("Vice President 3", "Vice President 3"),
            ("CEO", "CEO"),
            ("Chairperson", "Chairperson"),
            ("Vice Chairperson", "Vice Chairperson"),
            ("General Secretary", "General Secretary"),
            ("ASSHU Representative", "ASSHU Representative"),
            ("Assistant General Secretary", "Assistant General Secretary"),
            ("Treasurer", "Treasurer"),
            ("Secretariat", "Secretariat"),
            ("Secretary for Women", "Secretary for Women"),
            ("Western Representative", "Western Representative"),
            ("Eastern Representative", "Eastern Representative"),
            ("Northern Representative", "Northern Representative"),
            ("Central Representative", "Central Representative"),
            ("Kampala Representative", "Kampala Representative"),
            ("Committee Member", "Committee Member"),
        ],
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.first_name
