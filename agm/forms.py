from django import forms
from dashboard.models import *
from .models import *


class DelegatesForm(forms.ModelForm):
    class Meta:
        model = Delegates
        fields = [
            "first_name",
            "last_name",
            "zone",
            "photo",
            "contact",
            "region",
            "position",
            "email",
            "district",
            "gender",
            "school",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "school": forms.TextInput(attrs={"class": "form-control"}),
            "contact": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "zone": forms.Select(attrs={"class": "form-control"}),
            "region": forms.Select(attrs={"class": "form-control"}),
            "position": forms.Select(attrs={"class": "form-control"}),
            "district": forms.Select(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
        }



class ComisersForm(forms.ModelForm):
    class Meta:
        model = Comiser
        fields = [
            "first_name",
            "last_name",
            "comittee",
            "photo",
            "role",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "comittee": forms.TextInput(attrs={"class": "form-control"}),
            "contact": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.TextInput(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        }