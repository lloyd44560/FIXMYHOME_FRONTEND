from django.http import JsonResponse
from trader.models import Jobs, TraderRegistration, Leaves
from django.views.decorators.http import require_GET
from trader.decorators.traderOnly import trader_required

@require_GET
@trader_required
def calendar_events(request):
    events = []
    trader = TraderRegistration.objects.filter(user=request.user).first()

    # 🟦 JOB EVENTS
    jobs = Jobs.objects.filter(status="approved", trader=trader)
    for job in jobs:
        if job.start_date and job.end_date:
            duration = (job.end_date - job.start_date).days + 1
            events.append({
                "title": f"{job.job_code} ({duration} days)",
                "start": job.start_date.isoformat(),
                "end": job.end_date.isoformat(),
                "color": "#293272",  # deep blue
                "type": "job",
            })

    # Only fetch leaves if user is a team member
    if trader.isTeamMember:
        # 🟧 LEAVE EVENTS
        leaves = Leaves.objects.filter(team_member__user_id=request.user)
        for leave in leaves:
            if leave.start_date and leave.end_date:
                duration = (leave.end_date - leave.start_date).days + 1
                events.append({
                    "title": f"{leave.leave_type.title()} Leave ({duration} days)",
                    "start": leave.start_date.isoformat(),
                    "end": leave.end_date.isoformat(),
                    "color": "#EF7153",  # orange for leaves
                    "type": "leave",
                })

    return JsonResponse(events, safe=False)
