from django.urls import path
from . import views  # Import your views module

urlpatterns = [
    path('', views.home, name='home'),  # this calls views.home
    path('register/', views.register, name='register'),
    path('register_renter/', views.register_renter, name='register_renter'),
    path('login/', views.login, name='login'),
    path('welcome/', views.welcome, name='welcome'),
    path('login_renter/', views.login_view, name='login_renter'),

]