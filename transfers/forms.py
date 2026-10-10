from django import forms
from .models import *

# forms.py
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB

def validate_transfer_document(documents):
    if documents:
        if not documents.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Documents must be a PDF file.")
        if documents.size > MAX_DOCUMENT_SIZE:
            raise forms.ValidationError("File size must be under 10MB.")
    return documents


class AcceptTransferForm(forms.ModelForm):
    class Meta:
        model = TransferRequest
        fields = ["documents"]

    def clean_documents(self):
        documents = self.cleaned_data.get("documents")
        if not documents and self.instance.status == "paid":
            raise forms.ValidationError("A release letter is required to accept this transfer.")
        return validate_transfer_document(documents)


class InitiateTransferForm(forms.Form):
    phone_number = forms.CharField(max_length=15)
    documents = forms.FileField(required=False)

    def __init__(self, *args, athlete=None, **kwargs):
        super().__init__(*args, **kwargs)
        if athlete and athlete.status != "ACTIVE":
            self.fields["documents"].required = True

    def clean_documents(self):
        return validate_transfer_document(self.cleaned_data.get("documents"))

class TransferRejectionForm(forms.ModelForm):
    class Meta:
        model = TransferMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter reason for rejection...'}),
        }
        
        
