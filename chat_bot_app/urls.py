from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),  # GET → HTML-страница
    path('chat/', views.mistral_api, name='api_chat'),  # POST → API
]