from django import forms
from .models import *

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'topic', 'priority', 'content']
        
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "topic": forms.Select(attrs={"class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 7}),
        }
        
class TicketResponseForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['message']
        
        widgets = {
            
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 7}),
        }

