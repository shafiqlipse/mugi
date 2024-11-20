import django_filters
from .models import Trainee
from django import forms


class TraineeFilter(django_filters.FilterSet):

    zone = django_filters.ChoiceFilter(
        widget=forms.Select(attrs={"class": "form-control"})
    )
    region = django_filters.ChoiceFilter(
        widget=forms.Select(attrs={"class": "form-control"})
    )
    district = django_filters.ChoiceFilter(
        widget=forms.Select(attrs={"class": "form-control"})
    )
    gender = django_filters.ChoiceFilter(
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Trainee
        fields = [
            "district",
            "region",
            "zone",
            "gender",
        ]
