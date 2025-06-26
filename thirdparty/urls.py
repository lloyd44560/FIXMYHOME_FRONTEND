# thirdparty/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.thirdparty_register, name='thirdparty_register'),
    path('login/', views.thirdparty_login, name='thirdparty_login'),
    path('home/', views.thirdparty_home, name='thirdparty_home'),
    
    path('account/', views.third_party_account, name='third_party_account'),
]
