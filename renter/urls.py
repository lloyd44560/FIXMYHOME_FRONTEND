from django.urls import path
from . import views  # Import your views module

urlpatterns = [
    path('', views.home, name='home'),  # this calls views.home
]
