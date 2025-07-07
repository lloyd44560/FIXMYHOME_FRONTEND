from django.urls import path, include
from . import views  # Import your views module
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('', views.home, name='home'),  # this calls views.home
    path('', views.login_page, name='login'),  # Just renders login form
    path('register/', views.register, name='register'),
    path('register_renter/', views.register_renter, name='register_renter'),
    path('login_renter/', views.login_view, name='login_renter'),  # Handles form POST
    path('welcome/', views.welcome, name='welcome'),
    path('login_renter/', views.login_view, name='login_renter'),
    path('logout/', LogoutView.as_view(next_page='/login_renter/', http_method_names=['get', 'post']), name='logout'),

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


    path('social-auth/', include('social_django.urls', namespace='social')),
    path('login-error/', views.login_error, name='login_error'),
    
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),

    path('add-job/', views.add_job, name='add_job'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('edit-job/', views.edit_job, name='edit_job'),
    
    path('edit-room-condition/<int:pk>/json/', views.edit_room_condition_json, name='edit_room_condition_json'),
    path('edit-room-condition/', views.update_room_condition, name='update_room_condition'),


    path('edit-appliance-report/<int:pk>/json/', views.get_appliance_report_json, name='get_appliance_report_json'),
    path('update-appliance-report/', views.update_appliance_report, name='update_appliance_report'),

    path('change-password/', views.change_password, name='change_password'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
