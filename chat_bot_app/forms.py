from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='First Name')
    last_name = forms.CharField(max_length=30, required=True, label='Last Name')
    email = forms.EmailField(required=True, label='Email')
    birth_date = forms.DateField(required=True, label='Birth Date', widget=forms.DateInput(attrs={'type': 'date'}))
    avatar = forms.ImageField(required=False, label='Profile Photo')  # <-- Add this line

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'birth_date', 'password1', 'password2', 'avatar')