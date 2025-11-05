import django_filters
from .models import *
from django import forms
from django.db.models import Q


class TransferPaymentFilter(django_filters.FilterSet):

    transfer = django_filters.ModelChoiceFilter(
        queryset=TransferRequest.objects.all(),
        label="Transfer",
        widget=forms.Select(attrs={"class": "form-select js-example-basic-single"})
    )

    phone_number = django_filters.CharFilter(
        field_name="phone_number",
        lookup_expr="icontains",
        label="Phone Number",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter phone number"})
    )


    class Meta:
        model = TransferPayment
        fields = ["transfer",  "phone_number", "status"]

    def __init__(self, *args, **kwargs):
        super(TransferPaymentFilter, self).__init__(*args, **kwargs)
        for field_name, field in self.form.fields.items():
            field.widget.attrs.update({"class": "form-control"})