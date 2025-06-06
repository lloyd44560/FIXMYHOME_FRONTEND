from django.urls import path
from . import views  # Import your views module
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),  # this calls views.home
    path('register/', views.register, name='register'),
    path('register_renter/', views.register_renter, name='register_renter'),
    path('login/', views.login_page, name='login'),  # Just renders login form
    path('login_renter/', views.login_view, name='login_renter'),  # Handles form POST
    path('welcome/', views.welcome, name='welcome'),
    path('login_renter/', views.login_view, name='login_renter'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
]