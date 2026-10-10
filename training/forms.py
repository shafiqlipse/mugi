import re
from django import forms

from payments.models import Payment
from .models import Trainee, Season, Venue


class TraineesForm(forms.ModelForm):
    # Form-only field: saved on Payment, not on Trainee
    phone_number = Payment._meta.get_field("phone_number").formfield(
        label="Airtel Money Number",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. 0750123456",
            "inputmode": "tel",
             "form": "trainee_form",
        }),
    )

    class Meta:
        model = Trainee
        fields = [
            "first_name",
            "last_name",
            "contact",
            "email",
            "place",
            "district",
            "gender",
            "date_of_birth",
            "designation",
            "photo",
            "season",
            "venue",
            "course",
            "level",
            "residence_type",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "contact": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "place": forms.TextInput(attrs={"class": "form-control"}),
            "district": forms.Select(attrs={"class": "form-control js-example-basic-single"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "designation": forms.Select(attrs={"class": "form-control"}),
            "photo": forms.FileInput(attrs={"class": "form-control"}),
            "season": forms.Select(attrs={"class": "form-control"}),
            "venue": forms.Select(attrs={"class": "form-control"}),
            "course": forms.Select(attrs={"class": "form-control"}),
            "level": forms.Select(attrs={"class": "form-control"}),
            "residence_type": forms.Select(attrs={"class": "form-control"}),
        }



    # def clean_phone_number(self):
    #     digits = re.sub(r"\D", "", self.cleaned_data["phone_number"])
    #     if digits.startswith("256"):
    #         digits = digits[3:]
    #     digits = digits.lstrip("0")
    #     if not re.fullmatch(r"\d{9}", digits):
    #         raise forms.ValidationError("Enter a valid phone number, e.g. 0750123456.")
    #     return digits

  
