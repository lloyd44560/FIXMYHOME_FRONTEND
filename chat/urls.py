from django.urls import path
from . import views

urlpatterns = [
    path('chat/<slug:room_slug>/', views.chat_room, name='chat'),
    path('chat/<slug:room_slug>/fetch/', views.fetch_messages, name='fetch_messages'),
    path('chat/<slug:room_slug>/send/', views.send_message, name='send_message'),
        # General/default chat room
    path("chat/general/", views.chat_room, {"room_slug": "general"}, name="chat_general"),


       # User-specific job chats
    path("chat/jobs/", views.my_job_chats, name="my_job_chats"),

    # Single job chat thread
    path("chat/job_chat/<str:job_code>/", views.job_chat_room, name="job_chat_room"),
    path("chat/job_chat/<str:job_code>/fetch/", views.fetch_job_messages, name="fetch_job_messages"),
    path("chat/job_chat/<str:job_code>/send/", views.send_job_message, name="send_job_message"),

    # All jobs threads (admin or general view)
    path('all_jobs/', views.all_job_threads, name='all_job_threads'),

]