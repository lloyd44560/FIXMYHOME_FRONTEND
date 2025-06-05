from django.urls import path
from . import views  # Import your views module

urlpatterns = [
    path('register/', views.register, name='register'),
]
