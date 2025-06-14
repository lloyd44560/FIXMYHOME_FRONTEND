from django.urls import path, include
from . import views  # Import your views module
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('', views.home, name='home'),  # this calls views.home
    path('', views.login_page, name='login'),  # Just renders login form
    path('register/', views.register, name='register'),
    path('register_renter/', views.register_renter, name='register_renter'),
    path('login_renter/', views.login_view, name='login_renter'),  # Handles form POST
    path('welcome/', views.welcome, name='welcome'),
    path('login_renter/', views.login_view, name='login_renter'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='renter/password_reset_form.html',
        success_url='/password_reset/done/'
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='renter/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='renter/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='renter/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('social-auth/', include('social_django.urls', namespace='social')),
    path('send_reset_link/', views.send_reset_link, name='send_reset_link'),

    path('account/', views.renter_account, name='renter_account'),
    # path('messages/',  views.messages, name='renter_messages'),
    path('chat/', views.demo_chat, name='demo_chat'),  
    path('chat/<str:job_number>/', views.chat_thread, name='chat_thread'),  
    


]