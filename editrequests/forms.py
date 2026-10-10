from django import forms
from school.models import *
from .models import *



EDITABLE_ATHLETE_FIELDS = ['fname', 'mname', 'lname', 'lin', 'index_number', 'date_of_birth', 'gender']

class AthleteEditRequestForm(forms.ModelForm):
    fname = forms.CharField(required=False)
    mname = forms.CharField(required=False)
    lname = forms.CharField(required=False)
    lin = forms.CharField(required=False)
    index_number = forms.CharField(required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[("Male", "male"), ("Female", "female")], required=False)
    photo = forms.ImageField(required=False)

    phone_number = forms.CharField(
        label="Phone Number", max_length=15, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter phone number'})
    )

    class Meta:
        model = AthleteEditRequest
        fields = ['reason', 'supporting_document']
        widgets = {
            "supporting_document": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "placeholder": "Explain the reason for the edit request"}),
        }

    def __init__(self, *args, athlete=None, instance=None, **kwargs):
        self.athlete = athlete
        super().__init__(*args, instance=instance, **kwargs)
        self.is_resubmission = instance is not None and instance.pk is not None

    def clean(self):
        cleaned = super().clean()
        changes = {}
        for field in EDITABLE_ATHLETE_FIELDS:
            value = cleaned.get(field)
            if value in (None, ''):
                continue
            current = getattr(self.athlete, field)
            if value != current:
                changes[field] = str(value) if hasattr(value, 'isoformat') else value

        if not changes and not cleaned.get('photo'):
            raise forms.ValidationError("No changes were submitted.")

        if 'lin' in changes and Athlete.objects.filter(lin=changes['lin']).exclude(pk=self.athlete.pk).exists():
            self.add_error('lin', "This LIN is already in use.")
        if 'index_number' in changes and Athlete.objects.filter(index_number=changes['index_number']).exclude(pk=self.athlete.pk).exists():
            self.add_error('index_number', "This index number is already in use.")

        self._changes = changes
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.athlete = self.athlete
        instance.school = self.athlete.school
        instance.requested_changes = self._changes
        # refresh original_data against the athlete's CURRENT state,
        # not whatever it was on first submission — another approved
        # request may have changed the athlete since then
        instance.original_data = {field: str(getattr(self.athlete, field)) for field in self._changes}
        if self.cleaned_data.get('photo'):
            instance.new_photo = self.cleaned_data['photo']

        if self.is_resubmission:
            instance.resubmit()  # sets PENDING_REVIEW, clears reviewer/reviewed_at
        # fresh submissions stay PENDING_PAYMENT until the payment view flips them

        if commit:
            instance.save()
        return instance