import os
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from llama_cpp import Llama
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


# Путь к модели (файл лежит прямо в директории приложения)
MODEL_PATH = str(Path(settings.BASE_DIR) / "chat_bot_app" / "mistral-7b-instruct-v0.2.Q4_K_M.gguf")

# Проверка
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model file not found at: {MODEL_PATH}\n"
        f"Directory content: {os.listdir(Path(settings.BASE_DIR) / 'chat_bot_app')}"
    )

# Инициализация (ОБЯЗАТЕЛЬНО str() для llama_cpp)
MODEL = Llama(
    model_path=MODEL_PATH,  # Уже преобразовано в строку
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=20
)

def chat_view(request):
    """Отображает HTML-страницу чата (GET-запрос)"""
    return render(request, 'chat_bot_app/main.html')

@csrf_exempt
def mistral_api(request):
    """Обрабатывает сообщения чата (POST-запрос)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # System prompt
            system_message = "<|system|>\nYou are Synthia, a polite AI assistant.\n"
            user_message = f"<|user|>\n{data.get('message', '').strip()}\n<|assistant|>\n"
            prompt = system_message + user_message

            response = MODEL.create_completion(
                prompt,
                max_tokens=200,
                stop=["<|user|>", "<|system|>"],
                temperature=0.7
            )

            return JsonResponse({
                'reply': response['choices'][0]['text'].strip(),
                'status': 'success'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST allowed'}, status=400)

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
    return render(request, 'chat_bot_app/register.html', {'form': form})

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
    return render(request, 'chat_bot_app/login.html', {'form': form})

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
    return render(request, 'chat_bot_app/profile.html', {'form': form, 'profile': profile})