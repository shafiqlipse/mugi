from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from school.models import *
from payments.models import *


class TransferRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),    # created, awaiting payment
        ("paid", "Paid"),          # payment complete, awaiting next step
        ("accepted", "Accepted"),  # owning school accepted (active athletes only) + release letter
        ("rejected", "Rejected"),
        ("approved", "Approved"),
    ]
    
    requester = models.ForeignKey(
        School,
        related_name="requesting_school",
        on_delete=models.PROTECT,
        blank=True,
        null=True, db_index=True
    )
    owner = models.ForeignKey(
        School,
        related_name="owning_school",
        on_delete=models.PROTECT,
        blank=True,
        null=True, db_index=True
    )
    athlete = models.ForeignKey(
        Athlete,
        related_name="transferred_athlete",
        on_delete=models.PROTECT,
        blank=True,
        null=True, db_index=True
    )
    approver = models.ForeignKey(
        User,
        related_name="transfer_approver",
        on_delete=models.SET_NULL,
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
    rejected_at = models.DateTimeField(null=True, blank=True)
    season_year = models.PositiveIntegerField(db_index=True, editable=False, null=True, blank=True)
    is_archived = models.BooleanField(default=False, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["athlete", "season_year"],
                condition=models.Q(is_archived=False),
                name="one_active_transfer_per_athlete_per_season",
            )
        ]

    def __str__(self):
        return f"Transfer of {self.athlete}"

    def save(self, *args, **kwargs):
        if self.season_year is None:
            self.season_year = (self.requested_at or timezone.now()).year
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.athlete is None:
            return  # nothing to validate against yet
        season_year = (self.requested_at or timezone.now()).year
        existing_transfers = TransferRequest.objects.filter(
            athlete=self.athlete,
            season_year=season_year,
            is_archived=False,
        )
        if self.pk:
            existing_transfers = existing_transfers.exclude(pk=self.pk)
        if existing_transfers.exists():
            raise ValidationError("This athlete has already been transferred this season.")

    @property
    def requires_acceptance(self):
        """Active athletes need the owning school's acceptance; new/free-agent
        athletes skip straight from paid -> admin approval."""
        return self.athlete_id is not None and self.athlete.status != "NEW"

    def mark_payment_received(self):
        """Called from the Airtel callback once payment is confirmed."""
        if self.status != "pending":
            raise ValueError("Only pending transfers can be marked as paid.")

        if self.requires_acceptance:
            # Active athlete — owner still has to accept and upload a release letter.
            self.status = "paid"
        else:
            # Free agent — documents were already attached at initiation,
            # so payment confirmation IS the acceptance step.
            if not self.documents:
                raise ValueError("Free agent transfer is missing required documents.")
            self.status = "accepted"
            self.accepted_at = timezone.now()
        self.save()

    def accept_transfer(self):
        """Owning school accepts an active athlete's transfer (release letter required)."""
        if not self.requires_acceptance:
            raise ValueError("This athlete does not require owning-school acceptance.")
        if self.status != "paid":
            raise ValueError("Only paid transfers can be accepted.")
        if not self.documents:
            raise ValueError("A release letter must be uploaded to accept this transfer.")
        self.status = "accepted"
        self.accepted_at = timezone.now()
        self.save()

    def reject_transfer(self):
        if self.status not in ("paid", "accepted"):
            raise ValueError("Only paid or accepted transfers can be rejected.")
        self.status = "rejected"
        self.rejected_at = timezone.now()
        self.save()

    @transaction.atomic
    def approve_transfer(self, approver):
        """Now identical for both flows — only ever checks 'accepted'."""
        if self.status != "accepted":
            raise ValueError("Only accepted transfers can be approved.")
        if not self.documents:
            raise ValueError("Cannot approve transfer without documents.")
        if self.athlete is None or self.requester is None:
            raise ValueError("Transfer is missing athlete or requesting school")

        self.status = "approved"
        self.approved_at = timezone.now()
        self.approver = approver

        athlete = self.athlete
        athlete.school = self.requester
        athlete.save()
        self.save()

class TransferPayment(models.Model):
    transfer = models.OneToOneField(
        TransferRequest,
        related_name="payment",
        on_delete=models.CASCADE,
        db_index=True
    )
    payment = models.ForeignKey(
        Payment,
        related_name="transfer_payments",
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment} {self.transfer}"


class TransferMessage(models.Model):
    transfer = models.ForeignKey(TransferRequest, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(School)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from Transfers department about transfer of {self.transfer.athlete}"
    
  
            
            