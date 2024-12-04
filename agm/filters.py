import django_filters
from .models import *
from django import forms


class DelegateFilter(django_filters.FilterSet):

    zone = django_filters.ModelChoiceFilter(
        queryset=Zone.objects.all(), label="Zone"
    )
    region = django_filters.ModelChoiceFilter(
        queryset=Region.objects.all(), label="Region"
    )

    district = django_filters.ModelChoiceFilter(
        queryset=District.objects.all(), label="Position"
    )


    class Meta:
        model = Delegates
        fields = [
            "position",
            "region",
            "zone",
           
        ]
