# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
import json

from trader.models import TraderRegistration, TeamMember, Leaves

@csrf_exempt
def request_leave(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        leave_type = data.get("leave_type")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        reason = data.get("reason")

        try:
            team_member = TeamMember.objects.get(user=request.user)
            trader = team_member.trader

            leave = Leaves.objects.create(
                trader=trader,
                team_member=team_member,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
            )

            messages.success(request, 'Leave request submitted successfully.')
            return JsonResponse({"success": True, "message": "Leave request submitted successfully."})
        except TeamMember.DoesNotExist:
            messages.error(request, 'Team member not found.')
            return JsonResponse({"success": False, "error": "Team member not found."})

    messages.error(request, 'Invalid request method.')
    return JsonResponse({"success": False, "error": "Invalid request method."})
