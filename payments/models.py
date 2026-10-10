# payments/models.py
import re
from django.core.exceptions import ValidationError
from django.db import models

class Payment(models.Model):
    PAYMENT_TYPES = [
        ('REGISTRATION', 'Registration'),
        ('TRANSFER', 'Transfer'),
        ('EDIT', 'Edit'),
        ('TRAINING', 'Training'),
    ]
    STATUS_CHOICES = [('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')]

    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True) 
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.amount} ({self.payment_type})"

    def clean(self):
        if not re.match(r'^(073|075|074|070)\d{7}$', self.phone_number):
            raise ValidationError("Phone number must be a valid Airtel money number.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)