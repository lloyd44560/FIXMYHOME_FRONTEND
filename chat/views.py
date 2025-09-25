from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from django.core.paginator import Paginator  # import paginator


@login_required
def chat_room(request, room_name):
    search_query = request.GET.get('search', '') 

    # Must have a dynamic filter here, currently this is displaying all  registered users in auth.user
    # This will be dynamic based from the role of the logged in user
    
    # FOr this we need to determine the user role:
        # If the user is renter this will be the list of users to chat
        # If the user is agent this will be the list of users to chat
        # If the user is trader this will be the list of users to chat

    # For now all users muna

    users = User.objects.exclude(id=request.user.id) 

    # fetch messages between current user and selected room_name as in the username of the user 
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))  

    chats = chats.order_by('timestamp') 

    # build last messages per user
    user_last_messages = []
    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(receiver=request.user) & Q(sender=user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # sort by last_message timestamp
    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else timezone.make_aware(datetime.min),
        reverse=True
    )

    #  Paginate user list (10 per page) If the user has many chats
    paginator = Paginator(user_last_messages, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'chat.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': page_obj,  # paginated object
        'page_obj': page_obj,
        'search_query': search_query 
    })
