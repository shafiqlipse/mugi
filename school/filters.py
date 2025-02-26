import django_filters
from .models import *
from django import forms
from django.db.models import Q

class AthleteFilter(django_filters.FilterSet):
    gender = django_filters.ChoiceFilter(
        choices=[("Male", "Male"), ("Female", "Female")],
        label="Gender",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    school = django_filters.ModelChoiceFilter(
        queryset=School.objects.all(),
        label="School",
        widget=forms.Select(attrs={"class": "form-select js-example-basic-single"})
    )
    search = django_filters.CharFilter(
        method="filter_by_name",
        label="Name",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter name"})
    )
    index_number = django_filters.CharFilter(
        field_name="index_number",
        lookup_expr="icontains",
        label="Index Number",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter index number"})
    )

    class Meta:
        model = Athlete
        fields = ["gender", "school", "search", "index_number"]

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(Q(fname__icontains=value) | Q(mname__icontains=value))