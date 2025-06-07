from django.urls import path
from . import views  # Import your views module

urlpatterns = [
    path('register/', views.TraderRegistrationCreateView.as_view(), name='register_submit'),
]
