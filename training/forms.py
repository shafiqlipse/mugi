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
            "season",
            "photo",
            "contact",
            "course",
            "email",
            "district",
            "gender",
            "date_of_birth",
            "place",
            "designation",
            "level",
            "residence_type",
            "phone_number",
           
        ]
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Filter the championship queryset to only include active championships
            self.fields['season'].queryset = Season.objects.filter(status='Active')
            
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "school": forms.TextInput(attrs={"class": "form-control"}),
            "contact": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "place": forms.TextInput(attrs={"class": "form-control"}),         
            "venue": forms.Select(attrs={"class": "form-control"}),
            "season": forms.Select(attrs={"class": "form-control"}),
            "designation": forms.Select(attrs={"class": "form-control"}),
            "course": forms.Select(attrs={"class": "form-control"}),
            "district": forms.Select(attrs={"class": "form-control js-example-basic-single"}),
            "residence_type": forms.Select(attrs={"class": "form-control"}),
            "photo": forms.FileInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "level": forms.Select(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }
