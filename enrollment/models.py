from django.db import models
from accounts.models import *
from school.models import *


# Create your models here.
class SchoolEnrollment(models.Model):
    school = models.ForeignKey(
        School, related_name="enrollments", on_delete=models.CASCADE, db_index=True
    )
    championship = models.ForeignKey(
        Championship, related_name="school_enrollments", on_delete=models.CASCADE, limit_choices_to={'status': 'Active'}, db_index=True
    )
    sport = models.ForeignKey(
        Sport, related_name="athlete_enrollments", on_delete=models.CASCADE, db_index=True
    )
    level = models.CharField(max_length=144, blank=True, null=True, choices=(("District", "District"), ("Zone", "Zone"), ("National", "National")))
    enrollment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("school", "championship", "sport", "level")
        
    def __str__(self):
        return f"{self.school.name} - {self.championship.name}"


class AthleteEnrollment(models.Model):
    school_enrollment = models.ForeignKey(
        SchoolEnrollment,
        related_name="athlete_enrollments",  # Changed from "school_enrollments"
        on_delete=models.CASCADE, db_index=True
    )
    athletes = models.ManyToManyField(Athlete, db_index=True)
    enrollment_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    enrolled_by = models.ForeignKey(
        User, related_name="enrollments", on_delete=models.CASCADE, blank=True, null=True
    )
    def save(self, *args, **kwargs):
        # Check for duplicates before saving
        if self.pk:  # Only check if the instance already exists
            existing_athletes = set(self.athletes.values_list("id", flat=True))
            if len(existing_athletes) != self.athletes.count():
                raise ValidationError("An athlete cannot be added more than once.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.school_enrollment.school.name} - {self.school_enrollment.sport.name}"  # Fixed to use school_enrollment.sport
