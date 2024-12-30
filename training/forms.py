from django import forms
from dashboard.models import *
from .models import *


class TraineesForm(forms.ModelForm):
    class Meta:
        model = Trainee
        fields = [
            "first_name",
            "last_name",
            "venue",
     
            "photo",
            "contact",
            "discipline",
            "email",
            "district",
            "gender",
            "date_of_birth",
            "place",
            "designation",
            "course",
            "level",
         
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "school": forms.TextInput(attrs={"class": "form-control"}),
            "contact": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "place": forms.TextInput(attrs={"class": "form-control"}),
           
            "venue": forms.Select(attrs={"class": "form-control"}),
         
            "designation": forms.Select(attrs={"class": "form-control"}),
            "discipline": forms.Select(attrs={"class": "form-control"}),
            "district": forms.Select(attrs={"class": "form-control"}),
            "course": forms.Select(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "level": forms.Select(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }
