from django.urls import path
from . import views  # Import your views module

urlpatterns = [
    path('register/', views.register, name='register'),
    path('register_submit/', views.createRegisterTrader, name='register_submit'),
]
