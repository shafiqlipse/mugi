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

class SchoolFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="Name",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter name"})
    )
    district = django_filters.ModelChoiceFilter(
        queryset=District.objects.all(),
        label="District",
        widget=forms.Select(attrs={"class": "form-select js-example-basic-single"})
    )


    class Meta:
        model = School
        fields = ["district",  "search"]

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(center_number__icontains=value))

    def __init__(self, *args, **kwargs):
        super(SchoolFilter, self).__init__(*args, **kwargs)
        for field_name, field in self.form.fields.items():
            field.widget.attrs.update({"class": "form-control"})


class PaymentFilter(django_filters.FilterSet):

    school = django_filters.ModelChoiceFilter(
        queryset=School.objects.all(),
        label="School",
        widget=forms.Select(attrs={"class": "form-select js-example-basic-single"})
    )

    phone_number = django_filters.CharFilter(
        field_name="phone_number",
        lookup_expr="icontains",
        label="Phone Number",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter phone number"})
    )


    class Meta:
        model = Athlete
        fields = ["school",  "phone_number"]

    def __init__(self, *args, **kwargs):
        super(PaymentFilter, self).__init__(*args, **kwargs)
        for field_name, field in self.form.fields.items():
            field.widget.attrs.update({"class": "form-control"})