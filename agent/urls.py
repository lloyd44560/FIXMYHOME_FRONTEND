from django.urls import path
from . import views  # Import your views module

urlpatterns = [
    path('register/', views.AgentRegistrationCreateView.as_view(), name='register_agent'),
]
