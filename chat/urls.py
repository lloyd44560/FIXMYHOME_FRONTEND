from django.urls import path
from . import views

urlpatterns = [
    path('chat/<slug:room_slug>/', views.chat_room, name='chat'),
    path('chat/<slug:room_slug>/fetch/', views.fetch_messages, name='fetch_messages'),
    path('chat/<slug:room_slug>/send/', views.send_message, name='send_message'),
        # General/default chat room
    path("chat/general/", views.chat_room, {"room_slug": "general"}, name="chat_general"),
]