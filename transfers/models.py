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
        null=True,
    )
    owner = models.ForeignKey(
        School,
        related_name="owning_school",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    athlete = models.ForeignKey(
        Athlete,
        related_name="transferred_athlete",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
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
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    requested_at = models.DateTimeField(default=timezone.now)
    accepted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transfer of {self.athlete}"

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

        