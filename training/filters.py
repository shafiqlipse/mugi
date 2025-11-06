import django_filters
from django import forms
from django_filters import DateFromToRangeFilter
from django_filters.widgets import RangeWidget
from .models import Trainee, Level, Venue, Course  # adjust as necessary


class DateInput(forms.DateInput):
    input_type = "date"


class TraineeFilter(django_filters.FilterSet):
    gender = django_filters.ChoiceFilter(
        choices=[("Male", "Male"), ("Female", "Female")],
        label="Gender",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    level = django_filters.ModelChoiceFilter(
        queryset=Level.objects.all(),
        label="Level",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    venue = django_filters.ModelChoiceFilter(
        queryset=Venue.objects.all(),
        label="Venue",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    course = django_filters.ModelChoiceFilter(
        queryset=Course.objects.all(),
        label="Course",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    created_at = DateFromToRangeFilter(
        field_name="created_at",
        label="Created At (Range)",
        widget=RangeWidget(
            attrs={"type": "date", "class": "form-control"}
        ),
    )

    class Meta:
        model = Trainee
        fields = ["gender", "venue", "course", "level", "created_at"]
