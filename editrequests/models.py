from django.db import models
from school.models import *
from django.db import transaction
import os

# Create your models here.


class AthleteEditRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING_PAYMENT', 'Pending Payment'),   # created, awaiting payment confirmation
        ('PENDING_REVIEW', 'Pending Review'),     # paid, sitting in admin's queue
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
]
    OPEN_STATUSES = ('PENDING_PAYMENT', 'PENDING_REVIEW')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='edit_requests')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)

    # JSON field to hold all changes (field_name → new_value)
    requested_changes = models.JSONField()  # e.g. {"fname": "John", "lname": "Doe"}
    

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_PAYMENT')
    payment = models.OneToOneField('payments.Payment', on_delete=models.PROTECT, null=True, blank=True, related_name='athlete_edit_request')
    new_photo = models.ImageField(upload_to='athlete_photo_edits/', null=True, blank=True)
    original_data = models.JSONField(default=dict) 
    
    reason = models.TextField(blank=True, null=True)
    supporting_document = models.FileField(upload_to='edit_support_docs/', blank=True, null=True)

    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_edit_requests')
    reviewed_at = models.DateTimeField(blank=True, null=True)
    admin_comment = models.TextField(blank=True, null=True)
    


    def __str__(self):
        return f"{self.athlete} Edit Request ({self.status})"

    def apply_changes(self):
        
        for field, value in self.requested_changes.items():
            setattr(self.athlete, field, value)

        if self.new_photo:
            # delete the old file from storage so it doesn't orphan
            if self.athlete.photo:
                self.athlete.photo.delete(save=False)
            self.athlete.photo = self.new_photo

        self.athlete.save()
        self.status = 'APPROVED'
        self.reviewed_at = timezone.now()
        self.save()
        
    def get_absolute_url(self):
        return reverse('request_detail', args=[str(self.id)])   
    
    def mark_paid(self):
        # idempotent: payment callbacks get retried
        if self.status == 'PENDING_PAYMENT':
            self.status = 'PENDING_REVIEW'
            self.save(update_fields=['status'])

    def approve(self, reviewer):
        with transaction.atomic():
            athlete = Athlete.objects.select_for_update().get(pk=self.athlete_id)
            changes = {k: v for k, v in self.requested_changes.items() if k in EDITABLE_ATHLETE_FIELDS}

            # re-check uniqueness: another request may have taken the value since submission
            for f in ('lin', 'index_number'):
                if f in changes and Athlete.objects.filter(**{f: changes[f]}).exclude(pk=athlete.pk).exists():
                    raise ValidationError(f"{f} is now in use by another athlete.")

            for f, v in changes.items():
                setattr(athlete, f, v)

            old_photo = None
            if self.new_photo:
                old_photo = athlete.photo.name if athlete.photo else None
                athlete.photo.save(os.path.basename(self.new_photo.name), ContentFile(self.new_photo.read()), save=False)

            athlete.save()
            if old_photo:
                athlete.photo.storage.delete(old_photo)

            self.status = 'APPROVED'
            self.reviewed_by = reviewer
            self.reviewed_at = timezone.now()
            self.save()

def reject(self, reviewer, comment):
    timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
    entry = f"[{timestamp}] {reviewer}: {comment}"
    self.admin_comment = f"{self.admin_comment}\n{entry}" if self.admin_comment else entry
    self.status = 'REJECTED'
    self.reviewed_by = reviewer
    self.reviewed_at = timezone.now()
    self.save()
    
def resubmit(self):
    if self.status != 'REJECTED':
        raise ValueError("Only rejected requests can be resubmitted")
    self.status = 'PENDING_REVIEW'
    self.reviewed_by = None
    self.reviewed_at = None
    self.save()