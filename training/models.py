from django.db import models
from accounts.models import *


class Season(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    year = models.IntegerField()
    status = models.CharField( choices=[("Active", "Active"), ("Inactive", "Inactive")], max_length=10, default="Active" ,null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.name


class Venue(models.Model):
    name = models.CharField(max_length=50)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    courses = models.ManyToManyField('Course', blank=True)
    
    residential_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    non_residential_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField( choices=[("Active", "Active"), ("Inactive", "Inactive")], max_length=10, default="Active" ,null=True, blank=True)
    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=50)
    level = models.ForeignKey('Level', on_delete=models.CASCADE, null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"
    

    
class Level(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
# Create your models here.

class Trainee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    contact = models.CharField(max_length=50)
    place = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE,related_name=
                                 "trainee_district",)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
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
    residence_type = models.CharField(
        max_length=20,
        choices=[
            ("Residential", "Residential"),
            ("Non Residential", "Non Residential"),
        ],
    )
    

    # 💳 Payment-related fields
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Completed", "Completed"),
            ("Failed", "Failed"),
        ],
        default="Pending",
    )
    paid_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.transaction_id})"
    
    def save(self, *args, **kwargs):
        # Only recalculate if not a partial update (e.g. update_fields=['payment_status'])
        update_fields = kwargs.get('update_fields')
        if update_fields is None and self.venue:
            if self.residence_type == "Residential":
                self.amount = self.venue.residential_amount
            else:
                self.amount = self.venue.non_residential_amount
        super().save(*args, **kwargs)
        
        
        
class ITTFSchool(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
    
class ITTFTrainee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    contact = models.CharField(max_length=50)
    school = models.ForeignKey(ITTFSchool, on_delete=models.CASCADE, related_name="ittf_trainee_school")
    email = models.EmailField(max_length=50, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE,related_name=
                                 "ittf_trainee_district",)

    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female")],
    )

    photo = models.ImageField(upload_to="trainee_photos/")

    recommendation_letter = models.FileField(upload_to="recommendation_letters/")

    # 💳 Payment-related fields
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Completed", "Completed"),
            ("Failed", "Failed"),
        ],
        default="Pending",
    )
    paid_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.transaction_id})"



