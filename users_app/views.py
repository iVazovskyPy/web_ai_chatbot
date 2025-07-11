import os
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from pathlib import Path
from .forms import CustomUserCreationForm, ProfileForm
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from .models import Profile
from django.contrib.auth.decorators import login_required

# Create your views here.
def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            # Save birth_date somewhere if you have a custom user model or profile
            login(request, user)
            return redirect('chat')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users_app/register.html', {'form': form})

def login_view(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('chat')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('chat')
    else:
        form = AuthenticationForm()
    return render(request, 'users_app/login.html', {'form': form})

def logout_view(request):
    """Выход пользователя"""
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    """Просмотр и редактирование профиля пользователя"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile, user=request.user)
    return render(request, 'users_app/profile.html', {'form': form, 'profile': profile})