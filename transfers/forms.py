from django import forms
from .models import *


class AcceptTransferForm(forms.ModelForm):
    class Meta:
        model = TransferRequest
        fields = ["documents"]

    def clean_documents(self):
        documents = self.cleaned_data.get("documents")
        if not documents and self.instance.status == "pending":
            raise forms.ValidationError("Transfer documents are required.")
        if documents:
            if not documents.name.lower().endswith(".pdf"):
                raise forms.ValidationError("Only PDF files are allowed.")
            if documents.size > 10 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size must be under 5MB.")
        return documents



class TransferRejectionForm(forms.ModelForm):
    class Meta:
        model = TransferMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter reason for rejection...'}),
        }