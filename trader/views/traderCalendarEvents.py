from django.http import JsonResponse
from trader.models import Jobs
from trader.models import TraderRegistration

from django.views.decorators.http import require_GET
from trader.decorators.traderOnly import trader_required

@require_GET  # allow GET for FullCalendar
@trader_required
def calendar_events(request):
    events = []
    trader = TraderRegistration.objects.filter(user=request.user).first()
    jobs = Jobs.objects.filter(status="approved", trader=trader)

    for job in jobs:
        if job.start_date and job.end_date:
            duration = (job.end_date - job.start_date).days + 1  # include both start & end

            events.append({
                "title": f"{job.job_code} ({duration} days)",
                "start": job.start_date.isoformat(),
                "end": job.end_date.isoformat(),
            })
    return JsonResponse(events, safe=False)