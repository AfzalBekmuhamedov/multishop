from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class SignUpForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class":"form-control",
        "placeholder":"password"
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class":"form-control",
        "placeholder":"re-password"
    }))
    class Meta:
        model = User
        fields = ["username","first_name","phone"]
        widgets = {
            "username":forms.TextInput(attrs={
                "class":"form-control",
                "placeholder":"Username"
            }),
            "first_name":forms.TextInput(attrs={
                "class":"form-control",
                "placeholder":"First Name"
            }),
            "phone":forms.TextInput(attrs={
                "class":"form-control",
                "placeholder":"Phone Number"
            }),
        }

class SignInForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class":"form-control",
        "placeholder":"Username"
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class":"form-control",
        "placeholder":"Password"
    }))