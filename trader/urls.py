from django.urls import path
from . import views  # Import your views module

urlpatterns = [
    path('home/', views.TraderHomeView.as_view(), name='trader_home'),
    path('register/', views.TraderRegistrationCreateView.as_view(), name='register_submit'),
]
