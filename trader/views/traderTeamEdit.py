from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from trader.models import TeamMember
import json

@csrf_exempt  # (optional: use CSRF token instead if using form)
def edit_team_member(request, member_id):
    """Handle editing of a team member via fetch() POST"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            member = TeamMember.objects.get(pk=member_id)
            member.email = data.get('email', member.email)
            member.save()
            return JsonResponse({'success': True, 'message': 'Team member updated successfully.'})
        except TeamMember.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Member not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
