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
from trader.models import Jobs
import json


def get_user_role(user):
    if Renter.objects.filter(user=user).exists():
        return "Renter"
    elif TraderRegistration.objects.filter(email=user.email).exists():
        return "Trader"
    elif AgentRegister.objects.filter(email=user.email).exists():
        return "Agent"
    return "Unknown"


# -------------------- GENERAL CHAT --------------------
@login_required
def chat_room(request, room_slug):
    search_query = request.GET.get('search', '')

    if room_slug == "general":
        room_user = None
        chats = Message.objects.filter(receiver__isnull=True).order_by("timestamp")
    else:
        try:
            room_user = next(u for u in User.objects.exclude(id=request.user.id) if slugify(u.username) == room_slug)
        except StopIteration:
            return render(request, "not_found.html", status=404)

        chats = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=room_user)) |
            (Q(sender=room_user) & Q(receiver=request.user))
        ).order_by("timestamp")

        if search_query:
            chats = chats.filter(content__icontains=search_query)

    # Sidebar: all users
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

    users_with_roles.sort(
        key=lambda x: x["last_message"].timestamp if x["last_message"] else timezone.make_aware(timezone.datetime.min),
        reverse=True
    )

    paginator = Paginator(users_with_roles, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "chat.html", {
        "room_user": None if room_slug == "general" else room_user,
        "room_slug": room_slug,
        "chats": chats,
        "user_last_messages": page_obj,
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
        {"sender": msg.sender.username, "content": msg.content, "timestamp": msg.timestamp.strftime("%H:%M")}
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


# -------------------- JOB CHAT --------------------
@login_required
def job_chat_room(request, job_code):
    job = get_object_or_404(Jobs, job_code=job_code)

    trader_user = job.trader.user if job.trader and hasattr(job.trader, "user") else None
    renter_user = None
    try:
        renter_instance = Renter.objects.get(name=job.renter)
        renter_user = renter_instance.user
    except Renter.DoesNotExist:
        pass

    # Only participants can access
    if request.user not in [trader_user, renter_user]:
        return render(request, "403.html", status=403)

    chats = Message.objects.filter(job=job).order_by("timestamp")

    return render(request, "job_chat.html", {
        "job": job,
        "chats": chats,
        "room_slug": job.job_code,
        "room_user": trader_user if request.user == renter_user else renter_user,
    })


@login_required
def fetch_job_messages(request, job_code):
    job = get_object_or_404(Jobs, job_code=job_code)
    chats = Message.objects.filter(job=job).order_by("timestamp")

    messages = [{
        "sender": msg.sender.username,
        "content": msg.content,
        "timestamp": msg.timestamp.strftime("%b %d %H:%M")
    } for msg in chats]

    # Add priority info
    priority_label = "Urgent" if job.priority == 1 else "Non-Urgent"

    return JsonResponse({
        "messages": messages,
        "job_priority": priority_label,
        "job_code": job.job_code
    })

@login_required
def send_job_message(request, job_code):
    if request.method == "POST":
        job = get_object_or_404(Jobs, job_code=job_code)

        # Read JSON data from request
        try:
            data = json.loads(request.body)
            content = data.get("message", "").strip()
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        if content:
            # Choose receiver: any user in the job other than sender
            receiver = User.objects.exclude(id=request.user.id).first()
            msg = Message.objects.create(
                job=job,
                sender=request.user,
                receiver=receiver,
                content=content,
                timestamp=timezone.now(),
            )
            return JsonResponse({
                "sender": msg.sender.username,
                "content": msg.content,
                "timestamp": msg.timestamp.strftime("%b %d %H:%M"),
            })

        return JsonResponse({"error": "Empty message"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)

# -------------------- MY JOBS CHAT THREADS --------------------
@login_required
def my_job_chats(request):
    user = request.user
    jobs_as_trader = Jobs.objects.filter(trader__user=user)
    renter_instance = Renter.objects.filter(user=user).first()
    jobs_as_renter = Jobs.objects.filter(renter=renter_instance.name) if renter_instance else Jobs.objects.none()
    my_jobs = (jobs_as_trader | jobs_as_renter).distinct()

    job_previews = []
    for job in my_jobs:
        last_msg = Message.objects.filter(job=job).order_by('-timestamp').first()
        job_previews.append({
            "job": job,
            "last_message": last_msg.content if last_msg else "",
            "last_timestamp": last_msg.timestamp if last_msg else None
        })

    job_previews.sort(key=lambda x: x['last_timestamp'] or 0, reverse=True)
    return render(request, "job_chat.html", {"job_previews": job_previews})


# # -------------------- ALL JOB THREADS --------------------
# @login_required
# def all_job_threads(request):
#     all_jobs = Jobs.objects.all()
#     job_previews = []
#     for job in all_jobs:
#         last_msg = Message.objects.filter(job=job).order_by('-timestamp').first()
#         job_previews.append({
#             "job": job,
#             "last_message": last_msg.content if last_msg else "",
#             "last_timestamp": last_msg.timestamp if last_msg else None
#         })
#     job_previews.sort(key=lambda x: x['last_timestamp'] or 0, reverse=True)
#     return render(request, "job_chat.html", {"job_previews": job_previews})




# -------------------- ALL JOB THREADS --------------------


# WHen i click one of the jobs it opens up to a thread, it loads all the messages between the renter_instance if the logged in is renter and if the logged in user is trader, the message of all the threader are the one that loads


   # Jobs where the user is a trader
    # jobs_as_trader = Jobs.objects.filter(trader__user=user)

    # Jobs where the user is a renter
    # renter_instance = Renter.objects.filter(user=user).first()

    # I must have the ability to send messages and receive messages that all will be stored in the Message table thanks
@login_required
def all_job_threads(request):
    user = request.user

    # Identify role
    role = get_user_role(user)

    # Jobs where the user is involved (either trader or renter)
    jobs_as_trader = Jobs.objects.filter(trader__user=user)
    renter_instance = Renter.objects.filter(user=user).first()
    jobs_as_renter = Jobs.objects.filter(renter=renter_instance.name) if renter_instance else Jobs.objects.none()

    my_jobs = (jobs_as_trader | jobs_as_renter).distinct()

    job_previews = []
    for job in my_jobs:
        last_msg = Message.objects.filter(job=job).order_by("-timestamp").first()
        job_previews.append({
            "job": job,
            "last_message": last_msg.content if last_msg else "",
            "last_timestamp": last_msg.timestamp if last_msg else None,
        })

    job_previews.sort(key=lambda x: x["last_timestamp"] or timezone.make_aware(timezone.datetime.min), reverse=True)

    paginator = Paginator(job_previews, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "job_chat.html", {
        "job_previews": page_obj,
        "page_obj": page_obj,
    })