from django import forms
# from dashboard.models import *
from accounts.models import User
# from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm



# class SchoolRegistrationForm(UserCreationForm):
#     first_name = forms.CharField(max_length=255)
#     last_name = forms.CharField(max_length=255)
#     email = forms.EmailField(max_length=100)
#     phone = forms.CharField(max_length=20, required=False)

#     class Meta:
#         model = User
#         fields = [
#             "email",
#             "first_name",
#             "last_name",
#             "phone",
#             "username",
#             "password1",
#             "password2",
#             "is_school",
#         ]

from django import forms
from .models import User
from django.contrib.auth.hashers import make_password

class UserEditForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}),
        label="New Password"
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.password = make_password(new_password)
        if commit:
            user.save()
        return user
