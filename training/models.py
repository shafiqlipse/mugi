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
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="trainee_district")
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[("Male", "Male"), ("Female", "Female")])
    designation = models.CharField(max_length=20,   choices=[
            ("Student", "Student"),
            ("Primary Teacher", "Primary Teacher"),
            ("Secondary Teacher", "Secondary Teacher"),
            ("Other", "Other"),
        ],)
    photo = models.ImageField(upload_to="trainee_photos/")
    residence_type = models.CharField(max_length=20, choices=[
        ("Residential", "Residential"),
        ("Non Residential", "Non Residential"),
    ])

    payment = models.OneToOneField('payments.Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='trainee_payment')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField( choices=[("Active", "Active"), ("Inactive", "Inactive")], max_length=10, default="Inactive" ,null=True, blank=True)
    # transaction_id, amount, phone_number, payment_status, paid_at → REMOVED, now on Payment

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def calculate_amount(self):
        """Pure calculation, no save side-effects — call this explicitly when you need the fee."""
        if self.residence_type == "Residential":
            return self.venue.residential_amount
        return self.venue.non_residential_amount       
        
        

