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



# Create your models here.
class AthleticsEnrollment(models.Model):
    school = models.ForeignKey(
        School, related_name="enrollmentes", on_delete=models.CASCADE, db_index=True,null=True, blank=True
    )
    championship = models.ForeignKey(
        Championship, related_name="zone_enrollments", on_delete=models.CASCADE, limit_choices_to={'status': 'Active'}, db_index=True
    )
    sport = models.ForeignKey(
        Sport, related_name="athletics_enrollments", on_delete=models.CASCADE, db_index=True
    )
    district = models.ForeignKey(
        District, related_name="athletices_enrollments", on_delete=models.CASCADE, db_index=True
    )
    zone = models.ForeignKey(
        Zone, related_name="athletic_enrollments", on_delete=models.CASCADE, db_index=True
    )
    enrollment_date = models.DateTimeField(auto_now_add=True)


        
    def __str__(self):
        return f"{self.zone.name} - {self.championship.name}"
    
    
class AthleticsAthletes(models.Model):
    school_enrollment = models.ForeignKey(
        AthleticsEnrollment,
        related_name="athletics_enrollments",  # Changed from "school_enrollments"
        on_delete=models.CASCADE, db_index=True
    )
    athletes = models.ManyToManyField(Athlete, db_index=True)
    enrollment_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    enrolled_by = models.ForeignKey(
        User, related_name="enrollmentes", on_delete=models.CASCADE, blank=True, null=True
    )
    def save(self, *args, **kwargs):
        # Check for duplicates before saving
        if self.pk:  # Only check if the instance already exists
            existing_athletes = set(self.athletes.values_list("id", flat=True))
            if len(existing_athletes) != self.athletes.count():
                raise ValidationError("An athlete cannot be added more than once.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.school_enrollment.zone.name} - {self.school_enrollment.sport.name}"  # Fixed to use school_enrollment.sport



# Create your models here.
class U14thleticsEnrollment(models.Model):
    schoool = models.ForeignKey(
        School, related_name="u14enrollmentes", on_delete=models.CASCADE, db_index=True,null=True, blank=True
    )
    championship = models.ForeignKey(
        Championship, related_name="school_u14enrollments", on_delete=models.CASCADE, limit_choices_to={'status': 'Active'}, db_index=True
    )
    sport = models.ForeignKey(
        Sport, related_name="u14thletics_enrollments", on_delete=models.CASCADE, db_index=True
    )

    enrollment_date = models.DateTimeField(auto_now_add=True)


        
    def __str__(self):
        return f"{self.schoool.name} - {self.championship.name}"
    
    
class U14thleticsAthletes(models.Model):
    school_enrollment = models.ForeignKey(
        U14thleticsEnrollment,
        related_name="u14athletics_enrollments",  # Changed from "school_enrollments"
        on_delete=models.CASCADE, db_index=True
    )
    athletes = models.ManyToManyField(Athlete, db_index=True)
    enrollment_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    enrolled_by = models.ForeignKey(
        User, related_name="u14enrollmentes", on_delete=models.CASCADE, blank=True, null=True
    )
    def save(self, *args, **kwargs):
        # Check for duplicates before saving
        if self.pk:  # Only check if the instance already exists
            existing_athletes = set(self.athletes.values_list("id", flat=True))
            if len(existing_athletes) != self.athletes.count():
                raise ValidationError("An athlete cannot be added more than once.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.school_enrollment.schoool.name} - {self.school_enrollment.sport.name}"  # Fixed to use school_enrollment.sport

class screening_report(models.Model):
    enrollment = models.ForeignKey(
        SchoolEnrollment,
        related_name="screening_reports",  # Changed from "school_enrollments"
        on_delete=models.CASCADE, db_index=True
    )
    report = models.TextField()
    screened_by = models.ForeignKey(
        User, related_name="screenings", on_delete=models.CASCADE, blank=True, null=True
    )
    screened_at = models.DateTimeField(auto_now_add=True)


        
    def __str__(self):
        return f"{self.enrollment.school} - {self.enrollment.sport}"