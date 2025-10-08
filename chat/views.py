from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.utils.text import slugify
from .models import Message
from renter.models import Renter
from trader.models import TraderRegistration
from agent.models import AgentRegister
from django.core.paginator import Paginator


def get_user_role(user):
    if Renter.objects.filter(user=user).exists():
        return "Renter"
    elif TraderRegistration.objects.filter(email=user.email).exists():
        return "Trader"
    elif AgentRegister.objects.filter(email=user.email).exists():
        return "Agent"
    return "Unknown"

@login_required
def chat_room(request, room_slug):
    search_query = request.GET.get('search', '')

    if room_slug == "general":
        # General chat: use a dummy user or just None
        room_user = None
        # For general chat, messages without a receiver
        chats = Message.objects.filter(receiver__isnull=True).order_by("timestamp")

        # Sidebar: you may still want to show users
        all_users = User.objects.exclude(id=request.user.id)
        users_with_roles = []

        for u in all_users:
            role = get_user_role(u)
            last_message = Message.objects.filter(
                (Q(sender=request.user) & Q(receiver=u)) |
                (Q(sender=u) & Q(receiver=request.user))
            ).order_by("-timestamp").first()

            users_with_roles.append({
                "user": u,
                "role": role,
                "last_message": last_message,
                "slug": slugify(u.username)
            })

        # Sort sidebar by last message
        users_with_roles.sort(
            key=lambda x: x["last_message"].timestamp if x["last_message"] else timezone.make_aware(timezone.datetime.min),
            reverse=True
        )

        # Pagination
        paginator = Paginator(users_with_roles, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "chat.html", {
            "room_user": room_user,
            "room_slug": room_slug,
            "chats": chats,
            "user_last_messages": users_with_roles,  # send all
            "search_query": search_query,
        })

    else:
        # Map slug to actual user
        try:
            room_user = next(u for u in User.objects.exclude(id=request.user.id) if slugify(u.username) == room_slug)
        except StopIteration:
            return render(request, "not_found.html", status=404)

        # Chats between current user and the selected room user
        chats = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=room_user)) |
            (Q(sender=room_user) & Q(receiver=request.user))
        ).order_by("timestamp")

        if search_query:
            chats = chats.filter(content__icontains=search_query)

        # Sidebar: show ALL users (not filtered by role)
        all_users = User.objects.exclude(id=request.user.id)
        users_with_roles = []

        for u in all_users:
            role = get_user_role(u)
            last_message = Message.objects.filter(
                (Q(sender=request.user) & Q(receiver=u)) |
                (Q(sender=u) & Q(receiver=request.user))
            ).order_by("-timestamp").first()

            users_with_roles.append({
                "user": u,
                "role": role,
                "last_message": last_message,
                "slug": slugify(u.username)
            })

        # Sort sidebar by most recent conversation
        users_with_roles.sort(
            key=lambda x: x["last_message"].timestamp if x["last_message"] else timezone.make_aware(timezone.datetime.min),
            reverse=True
        )

        paginator = Paginator(users_with_roles, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "chat.html", {
            "room_user": room_user,
            "room_slug": room_slug,
            "chats": chats,
            "user_last_messages": users_with_roles,  # show all
            "page_obj": page_obj,
            "search_query": search_query,
        })


@login_required
def fetch_messages(request, room_slug):
    try:
        room_user = next(u for u in User.objects.exclude(id=request.user.id) if slugify(u.username) == room_slug)
    except StopIteration:
        return JsonResponse({"error": "User not found"}, status=404)

    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=room_user)) |
        (Q(sender=room_user) & Q(receiver=request.user))
    ).order_by("timestamp")

    messages = [
        {
            "sender": msg.sender.username,
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%H:%M"),
        }
        for msg in chats
    ]
    return JsonResponse({"messages": messages})


@login_required
def send_message(request, room_slug):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        room_user = next(u for u in User.objects.exclude(id=request.user.id) if slugify(u.username) == room_slug)
    except StopIteration:
        return JsonResponse({"error": "User not found"}, status=404)

    import json
    data = json.loads(request.body)
    content = data.get("message", "").strip()
    if not content:
        return JsonResponse({"error": "Empty message"}, status=400)

    msg = Message.objects.create(sender=request.user, receiver=room_user, content=content)
    return JsonResponse({
        "sender": msg.sender.username,
        "content": msg.content,
        "timestamp": msg.timestamp.strftime("%H:%M")
    })
