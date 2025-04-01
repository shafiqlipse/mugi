from django.db import models

# Create your models here.
class Zonalchair(models.Model):
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=100)
    zone = models.ForeignKey("accounts.Zone", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, blank=True, null=True)  
    status = models.CharField(
        max_length=10, choices=[
             ("ACTIVE", "ACTIVE"), ("INACTIVE", "INACTIVE")
        ],
        null=True, blank=True, default="INACTIVE", db_index=True
    )
    def __str__(self):
        return f"{self.fname} {self.lname}" 
# Compare this snippet from usssa/accounts/views.py: