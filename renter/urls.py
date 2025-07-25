from django.urls import path, include
from . import views  # Import your views module
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import renter_actions
from .renter_actions import (
    PropertyListView,
)

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

    path('login-error/', views.login_error, name='login_error'),
    path('no-account/', TemplateView.as_view(template_name='no_account.html'), name='no_account'),

    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),

    path('add-job/', views.add_job, name='add_job'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('edit-job/', views.edit_job, name='edit_job'),

    path('edit-room-condition/<int:pk>/json/', views.edit_room_condition_json, name='edit_room_condition_json'),
    path('edit-room-condition/', views.update_room_condition, name='update_room_condition'),


    path('edit-appliance-report/<int:pk>/json/', views.get_appliance_report_json, name='get_appliance_report_json'),
    path('update-appliance-report/', views.update_appliance_report, name='update_appliance_report'),

    path('change-password/', views.change_password, name='change_password'),


    path('add-property/', renter_actions.add_property, name='add_property'),
    path('delete-property/<int:id>/', renter_actions.delete_property, name='delete_property'),
    path('unlink-property/<int:id>/', renter_actions.unlink_property, name='unlink_property'),
    path('edit-property/<int:id>/', renter_actions.edit_property, name='edit_property'),

    # for property

    path('report/add/', views.add_standard_report, name='add_standard_report'),
    path('report/edit/<int:id>/', views.edit_standard_report, name='edit_standard_report'),
    path('report/delete/<int:id>/', views.delete_standard_report, name='delete_standard_report'),



    path('properties/', PropertyListView.as_view(), name='property_list'),


    path('jobs/', renter_actions.list_jobs, name='job_list'),
    path('jobs/add/', renter_actions.add_job, name='add_job'),
    path('jobs/edit/<int:id>/', renter_actions.edit_job, name='edit_job'),
    path('jobs/delete/<int:id>/', renter_actions.delete_job, name='delete_job'),


    path('standard-reports/', renter_actions.standard_report_list, name='standard_report_list'),
    path('standard-reports/add/', renter_actions.add_standard_report, name='add_standard_report'),
    path('standard-reports/edit/<int:pk>/', renter_actions.edit_standard_report, name='edit_standard_report'),
    path('standard-reports/delete/<int:pk>/', renter_actions.delete_standard_report, name='delete_standard_report'),

    path('rooms/', renter_actions.renter_room_list, name='renter_room_list'),
    path('rooms/add/', renter_actions.add_renter_room, name='add_renter_room'),
    path('rooms/<int:pk>/edit/', renter_actions.edit_renter_room, name='edit_renter_room'),
    path('rooms/<int:pk>/delete/', renter_actions.delete_renter_room, name='delete_renter_room'),

    path('rooms/<int:room_id>/area/add/', renter_actions.add_area_condition, name='add_area_condition'),
    path('areas/<int:pk>/edit/', renter_actions.edit_area_condition, name='edit_area_condition'),
    path('areas/<int:pk>/delete/', renter_actions.delete_area_condition, name='delete_area_condition'),

    path('renter-rooms/', renter_actions.renter_room_list, name='renter_room_list'),


    # path('appliance-reports/', renter_actions.appliance_report_list, name='appliance_report_list'),

    # path('appliance-reports/edit/<int:pk>/', renter_actions.edit_appliance_report, name='edit_appliance_report'),
    # path('appliance-reports/delete/<int:pk>/', renter_actions.delete_appliance_report, name='delete_appliance_report'),


    path('appliance-reports/', renter_actions.appliance_report_list, name='appliance_report_list'),
    path('appliance-reports/add/', renter_actions.add_appliance_report, name='add_appliance_report'),
    path('appliance-reports/edit/<int:report_id>/', renter_actions.edit_appliance_report, name='edit_appliance_report'),
    path('appliance-reports/delete/<int:report_id>/', renter_actions.delete_appliance_report, name='delete_appliance_report'),

    path('condition-report/', views.condition_report_view, name='condition_report_view'),
    path('condition-report/save-all/', views.save_condition_report_all, name='save_condition_report_all'),

    # path('accounts/', include('allauth.urls')),  # django-allauth routes
    # path('', TemplateView.as_view(template_name="renter/home.html"), name='home'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
