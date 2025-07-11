import os
import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from llama_cpp import Llama
from django.conf import settings
from pathlib import Path
from django.shortcuts import redirect


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
