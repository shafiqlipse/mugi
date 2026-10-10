import django_filters
from .models import *
from school.models import School,Athlete
from django import forms
from django.db.models import Q

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
            
            
       
