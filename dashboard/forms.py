from django import forms
from accounts.models import *


class ChampionshipForm(forms.ModelForm):
    class Meta:
        model = Championship
        fields = [
            "name",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }
class SportForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = [
            "name",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
        }
        # """ "season": forms.Select(attrs={"class": "form-control"}),
        # "competition": forms.Select(attrs={"class": "form-control"}),
        # "stage": forms.Select(attrs={"class": "form-control"}),
        # "status": forms.Select(attrs={"class": "form-control"}),
        # "group": forms.TextInput(attrs={"class": "form-control"}),
        # "venue": forms.TextInput(attrs={"class": "form-control"}),
        # "team1": forms.Select(attrs={"class": "form-control"}),
        # "team2": forms.Select(attrs={"class": "form-control"}),
        # "team1_score": forms.NumberInput(attrs={"class": "form-control"}),
        # "team2_score": forms.NumberInput(attrs={"class": "form-control"}),
