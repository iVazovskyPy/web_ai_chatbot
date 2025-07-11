from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),  # Registration page
    path('login/', views.login_view, name='login'),  # Login page
    path('logout/', views.logout_view, name='logout'),  # Logout page
    path('profile/', views.profile_view, name='profile'),  # User profile page
]