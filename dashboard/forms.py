from django import forms
from accounts.models import *
from .models import *


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




class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = [
            "title",
            "content",
            "end_date",
            "banner",
 
        ]

        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 7}),
            "end_date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),  
        }
