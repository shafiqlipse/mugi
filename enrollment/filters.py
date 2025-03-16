import django_filters
from .models import SchoolEnrollment
from school.models import School
from accounts.models import Championship,Sport
from django import forms

class SchoolEnrollmentFilter(django_filters.FilterSet):
    school = django_filters.ModelChoiceFilter(
        queryset=School.objects.all(),
        label="School",
        widget=forms.Select(attrs={"class": "form-control js-example-basic-single"})
    )
    championship = django_filters.ModelChoiceFilter(
        queryset=Championship.objects.all(),
        label="Championship",
        widget=forms.Select(attrs={"class": "form-control"})
    )
    sport = django_filters.ModelChoiceFilter(
        queryset=Sport.objects.all(),
        label="Sport",
        widget=forms.Select(attrs={"class": "form-control js-example-basic-single"})
    )
    level = django_filters.ChoiceFilter(
        choices=[("District", "District"), ("Zone", "Zone"), ("National", "National")],
        label="Level",
      
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = SchoolEnrollment
        fields = [
            "school",
            "championship",
            "sport",
            "level",
        ]  # Add all fields you want to filter on
 