from django.http import JsonResponse
from trader.models import Bidding

def get_bidding(request, job_id):
    bids = Bidding.objects.filter(jobs_id=job_id)
    return JsonResponse({
        "success": True,
        "bids": [
            {
                "id": bid.id,
                "trader": str(bid.trader),
                "team_member": str(bid.team_member),
                "created_at": bid.created_at.strftime("%Y-%m-%d %H:%M"),
                "status": bid.jobs.status.title(),
            }
            for bid in bids
        ]
    })
