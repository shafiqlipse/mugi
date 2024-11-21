import django_filters
from .models import Delegates
from django import forms


class DelegateFilter(django_filters.FilterSet):

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
        model = Delegates
        fields = [
            "district",
            "region",
            "zone",
            "gender",
        ]
