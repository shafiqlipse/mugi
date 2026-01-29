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


class ScreeningReportForm(forms.ModelForm):
    
    class Meta:
        model = screening_report
        fields = ["report"]
            
        widgets = {
                "report": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
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


class U14AthleticsEnrollmentForm(forms.ModelForm):
    class Meta:
        model = U14thleticsEnrollment
        fields = [
            "championship",
            "sport",
            "schoool",
        ]
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Filter the championship queryset to only include active championships
            self.fields['championship'].queryset = Championship.objects.filter(status='Active')
            
        widgets = {
            "championship": forms.Select(attrs={"class": "form-control"}),
            "sport": forms.Select(attrs={"class": "form-control"}),
            "schoool": forms.Select(attrs={"class": "form-control js-example-basic-single"}),
        }


class U14AthleticsAthletesForm(forms.ModelForm):
    athletes = forms.ModelMultipleChoiceField(
        queryset=Athlete.objects.filter(status="ACTIVE"),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = U14thleticsAthletes
        fields = ["athletes"]
