from django import forms
from dashboard.models import *
from .models import *


class SchoolEnrollmentForm(forms.ModelForm):
    class Meta:
        model = SchoolEnrollment
        fields = [
            "championship",
            "sport",
            "level",
        ]
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Filter the championship queryset to only include active championships
            self.fields['championship'].queryset = Championship.objects.filter(status='Active')
            
        widgets = {
            "championship": forms.Select(attrs={"class": "form-control"}),
            "sport": forms.Select(attrs={"class": "form-control"}),
            "level": forms.Select(attrs={"class": "form-control"}),
        }


class AthleteEnrollmentForm(forms.ModelForm):
    athletes = forms.ModelMultipleChoiceField(
        queryset=Athlete.objects.filter(status="ACTIVE"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = AthleteEnrollment
        fields = ["athletes"]


class AthleticsEnrollmentForm(forms.ModelForm):
    class Meta:
        model = AthleticsEnrollment
        fields = [
            "championship",
            "sport",
            "zone",
            "district",
        ]
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Filter the championship queryset to only include active championships
            self.fields['championship'].queryset = Championship.objects.filter(status='Active')
            
        widgets = {
            "championship": forms.Select(attrs={"class": "form-control"}),
            "sport": forms.Select(attrs={"class": "form-control"}),
            "level": forms.Select(attrs={"class": "form-control"}),
            "zone": forms.Select(attrs={"class": "form-control"}),
            "district": forms.Select(attrs={"class": "form-control"}),
        }


class AthleticsAthletesForm(forms.ModelForm):
    athletes = forms.ModelMultipleChoiceField(
        queryset=Athlete.objects.filter(status="ACTIVE"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = AthleticsAthletes
        fields = ["athletes"]
