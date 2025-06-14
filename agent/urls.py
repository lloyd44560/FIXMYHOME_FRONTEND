from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views  # Import your views module

urlpatterns = [
    path('home/', views.AgentHomeView.as_view(), name='home_agent'),
    path('register/', views.AgentRegistrationCreateView.as_view(), name='register_agent'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout_agent'),
]
