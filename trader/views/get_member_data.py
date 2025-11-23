from django.http import JsonResponse, Http404
from trader.models import TeamMember  # adjust import as needed

def get_member_data(request, member_id):
    try:
        member = TeamMember.objects.get(pk=member_id)
    except TeamMember.DoesNotExist:
        raise Http404("Member not found")

    data = {
        "id": member.id,
        "name": member.teamName,
        "image": "https://randomuser.me/api/portraits/men/32.jpg",
        "role": member.position,
        "availability": "Available soon",  # or member.availability if exists
        "current_job": "Ongoing: Building Maintenance",  # optional, dynamic later
        "job_date": "Nov 2, 2025",
        "labour_per_hour": member.labour_rate_per_hour or 0.00,
        "callout_rate": member.callout_rate or 0.00,
    }
    print(data, '===============================>>>')
    return JsonResponse(data)