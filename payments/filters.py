import django_filters
from .models import *
from school.models import School,Athlete
from django import forms
from django.db.models import Q


class PaymentFilter(django_filters.FilterSet):

    
    school = django_filters.ModelChoiceFilter(
        queryset=School.objects.all(),
        label="School",
        empty_label="All schools",
        widget=forms.Select(attrs={"class": "form-select js-example-basic-single"}),
    )

    payment_type = django_filters.ChoiceFilter(
        choices=[ ('REGISTRATION', 'Registration'),
                ('TRANSFER', 'Transfer'),
                ('EDIT', 'Edit'),
                ('TRAINING', 'Training'),],  # see note below
        label="Payment Type",
        empty_label="All types",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = django_filters.ChoiceFilter(
        choices=[ ('PENDING', 'PENDING'),
                ('COMPLETED', 'COMPLETED'),
                ('FAILED', 'FAILED'),],  # see note below
        label="Status",
        empty_label="All types",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    phone_number = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Phone Number",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter phone number"}),
    )

    class Meta:
        model = Payment
        fields = ["school", "payment_type", "phone_number","status"]
