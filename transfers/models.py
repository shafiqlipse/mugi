from django.db import models
from accounts.models import User
from school.models import *

from django.core.validators import FileExtensionValidator
from django.utils import timezone


class TransferRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("approved", "Approved"),
    ]
    requester = models.ForeignKey(
        School,
        related_name="requesting_school",
        on_delete=models.CASCADE,
        blank=True,
        null=True, db_index=True
    )
    owner = models.ForeignKey(
        School,
        related_name="owning_school",
        on_delete=models.CASCADE,
        blank=True,
        null=True, db_index=True
    )
    athlete = models.ForeignKey(
        Athlete,
        related_name="transferred_athlete",
        on_delete=models.CASCADE,
        blank=True,
        null=True, db_index=True
    )
    approver = models.ForeignKey(
        User,
        related_name="transfer_approver",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    documents = models.FileField(
        upload_to="transfer_documents/",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending", db_index=True)
    requested_at = models.DateTimeField(default=timezone.now)
    accepted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transfer of {self.athlete}"

    def clean(self):
        super().clean()
        current_year = self.requested_at.year if self.requested_at else timezone.now().year
        existing_transfers = TransferRequest.objects.filter(
            athlete=self.athlete,
            requested_at__year=current_year
        )
        if self.pk:
            existing_transfers = existing_transfers.exclude(pk=self.pk)

        if existing_transfers.exists():
            raise ValidationError("This athlete has already been transferred this year.")

    def accept_transfer(self):
        """Mark transfer as accepted and set the timestamp."""
        self.status = "accepted"
        self.accepted_at = timezone.now()
        self.save()

    def reject_transfer(self):
        """Mark transfer as rejected."""
        self.status = "rejected"
        self.save()

    def approve_transfer(self,approver):
        """Final approval by the chief, transfer the athlete to the requesting school."""
        if self.status != "accepted":
            raise ValueError("Only accepted transfers can be approved")

        if not self.documents:
            raise ValueError("Cannot approve transfer without documents")

        # Update status and timestamp
        self.status = "approved"
        self.approved_at = timezone.now()
        self.approver = approver

        # Update athlete's school
        athlete = self.athlete
        athlete.school = self.requester

        # Save both objects
        athlete.save()
        self.save()

class TransferMessage(models.Model):
    transfer = models.ForeignKey(TransferRequest, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(School)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from Transfers department about transfer of {self.transfer.athlete}"
    
    
    
class TransferPayment(models.Model):
    transfer = models.OneToOneField(
        TransferRequest,
        related_name="payment",
        on_delete=models.CASCADE,
        db_index=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    status = models.CharField(
        max_length=20, 
        choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed')], 
        default='PENDING'
    )
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    method = models.CharField(max_length=50, blank=True, null=True)  # e.g., M-Pesa, Stripe, Bank
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
            return f"{self.transaction_id} - {self.amount} {self.transfer}"
        
    def clean(self):
            """Validate phone number format."""
            if not re.match(r'^(075|074|070)\d{7}$', self.phone_number):
                raise ValidationError("Phone number must a valid Airtel money number.")

    def save(self, *args, **kwargs):
            """Ensure validation before saving."""
            self.clean()
            super().save(*args, **kwargs)