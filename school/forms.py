from django import forms
from accounts.models import *
from school.models import *


class SchoolProfileForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
            "name",
            "emis_number",
            "center_number",
            "badge",
            "district",
            "fname",
            "lname",
            "nin",
            "photo",
            "phone_number",
            "email",
            "gender",
            "date_of_birth",
            "gfname",
            "glname",
            "gnin",
            "gphoto",
            "gphone",
            "gemail",
            "ggender",
            "gdate_of_birth",
        ]

        widgets = {
            # "badge": ImageCropWidget,
            # "photo": ImageCropWidget,
            # "gphoto": ImageCropWidget,
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "emis_number": forms.TextInput(attrs={"class": "form-control"}),
            "center_number": forms.TextInput(attrs={"class": "form-control"}),
            "district": forms.Select(attrs={"class": "form-control"}),
            #    --------------------------------------
            "fname": forms.TextInput(attrs={"class": "form-control"}),
            "lname": forms.TextInput(attrs={"class": "form-control"}),
            "nin": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            #    --------------------------------------
            "gfname": forms.TextInput(attrs={"class": "form-control"}),
            "glname": forms.TextInput(attrs={"class": "form-control"}),
            "gnin": forms.TextInput(attrs={"class": "form-control"}),
            "gphone_number": forms.TextInput(attrs={"class": "form-control"}),
            "gemail": forms.TextInput(attrs={"class": "form-control"}),
            "ggender": forms.Select(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "gdate_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super(SchoolProfileForm, self).__init__(*args, **kwargs)
        self.fields["badge"].widget.attrs["onchange"] = "displayImage(this);"

    def __init__(self, *args, **kwargs):
        super(SchoolProfileForm, self).__init__(*args, **kwargs)
        self.fields["photo"].widget.attrs["onchange"] = "displayImage(this);"

    def __init__(self, *args, **kwargs):
        super(SchoolProfileForm, self).__init__(*args, **kwargs)
        self.fields["gphoto"].widget.attrs["onchange"] = "displayImage(this);"


class OfficialForm(forms.ModelForm):
    class Meta:
        model = school_official
        fields = [
            "fname",
            "lname",
            "nin",
            "photo",
            "phone_number",
            "email",
            "gender",
            "date_of_birth",
            "role",
        ]

        widgets = {
            # "photo": ImageCropWidget,
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "fname": forms.TextInput(attrs={"class": "form-control"}),
            "lname": forms.TextInput(attrs={"class": "form-control"}),
            "nin": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(OfficialForm, self).__init__(*args, **kwargs)
        self.fields["photo"].widget.attrs["onchange"] = "displayImage(this);"


class NewAthleteForm(forms.ModelForm):
    class Meta:
        model = Athlete
        fields = [
            "fname",
            "mname",
            "lname",
            "lin",
            "index_number",
            "sport",
            "date_of_birth",
            "gender",
            "classroom",
            "physic",
            "nationality",
            "refugee",
            "photo",
            "uce_certificate",
            "ple_certificate",
            "student_pass",
            "student_visa",
            "bursary",
            "sponsorship",
            "student_pass_code",
            "uneb_code",
            "uneb_eq_results",
            "refugee_card",
            "Parent_fname",
            "Parent_lname",
            "parent_phone_number",
            "parent_nin",
            "address",
            "relationship",
        ]
        widgets = {
            #    --------------------------------------
            "fname": forms.TextInput(attrs={"class": "form-control"}),
            "mname": forms.TextInput(attrs={"class": "form-control"}),
            "lname": forms.TextInput(attrs={"class": "form-control"}),
            "lin": forms.TextInput(attrs={"class": "form-control"}),
            "student_pass_code": forms.TextInput(attrs={"class": "form-control"}),
            "uneb_code": forms.TextInput(attrs={"class": "form-control"}),
            "index_number": forms.TextInput(attrs={"class": "form-control"}),
            "Parent_fname": forms.TextInput(attrs={"class": "form-control"}),
            "Parent_lname": forms.TextInput(attrs={"class": "form-control"}),
            "parent_phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "parent_nin": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "sport": forms.Select(attrs={"class": "form-control"}),
            "nationality": forms.Select(attrs={"class": "form-control"}),
            "refugee": forms.Select(attrs={"class": "form-control"}),
            "physic": forms.Select(attrs={"class": "form-control"}),
            "classroom": forms.Select(attrs={"class": "form-control"}),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "relationship": forms.Select(attrs={"class": "form-control"}),
            "sponsorship": forms.Select(attrs={"class": "form-control"}),
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }


class ScreenForm(forms.ModelForm):
    class Meta:
        model = Screening
        fields = [
            "status",
            "description",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }



class PaymentForm(forms.Form):
    phone_number = forms.CharField(
        label="Phone Number",
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Airtel Money phone number'})
    )
    athletes = forms.ModelMultipleChoiceField(
        queryset=Athlete.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        if school:
            # Fetch only unpaid learners in the specific class
            self.fields['athletes'].queryset = Athlete.objects.filter(
                school=school, status='NEW'
            )
            # Customize labels to include the amount for each learner
            self.fields['athletes'].label_from_instance = lambda obj: f"{obj.fname} (Amount: 3000)"