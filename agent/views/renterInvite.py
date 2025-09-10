import uuid
from django.core.mail import send_mail
from urllib.parse import urlencode
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import datetime
from django.conf import settings

from django.views.generic.edit import FormView

from agent.forms import InvitationForm
from agent.models import AgentRegister

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from agent.decorators.agentOnly import agent_required

@method_decorator(login_required, name='dispatch')
class InviteRenterView(FormView):
    template_name = 'components/home/invitationForm.html'
    form_class = InvitationForm
    success_url = reverse_lazy("renter_invitation")

    def get_initial(self):
        initial = super().get_initial()
        # Convert lease_start and lease_end from mm/dd/yyyy to YYYY-MM-DD for form
        lease_start = self.request.GET.get('property_lease_start', '')
        lease_end = self.request.GET.get('property_lease_end', '')
        try:
            if lease_start and '/' in lease_start:
                lease_start = datetime.strptime(lease_start, '%m/%d/%Y').strftime('%Y-%m-%d')
        except ValueError:
            lease_start = ''
        try:
            if lease_end and '/' in lease_end:
                lease_end = datetime.strptime(lease_end, '%m/%d/%Y').strftime('%Y-%m-%d')
        except ValueError:
            lease_end = ''

        initial.update({
            'name': self.request.GET.get('name', ''),
            'email': self.request.GET.get('email', ''),
            'renter_contact': self.request.GET.get('renter_contact', ''),
            'property_id': self.request.GET.get('property_id', ''),
            'property_name': self.request.GET.get('property_name', ''),
            'address': self.request.GET.get('property_address', ''),
            'lease_start': lease_start,
            'lease_end': lease_end,
            'rent': self.request.GET.get('property_rent', ''),
            'status': self.request.GET.get('property_status', ''),
        })
        return initial

    def form_valid(self, form):
        # Get the data of the logged-in Agent
        try:
            agent = AgentRegister.objects.get(user=self.request.user)
        except AgentRegister.DoesNotExist:
            agent = None

        # Get form data
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        renter_contact = form.cleaned_data["renter_contact"]
        property_id = form.cleaned_data["property_id"]
        property_name = form.cleaned_data["property_name"]
        address = form.cleaned_data["address"]
        lease_start = form.cleaned_data["lease_start"]
        lease_end = form.cleaned_data["lease_end"]
        rent = form.cleaned_data["rent"]
        status = form.cleaned_data["status"]

        token = str(uuid.uuid4())

        # Construct params for the invitation link
        params = urlencode({
            'token': token,
            'name': name,
            'email': email,
            'agent_id': agent.id if agent else '',
            'property_id': property_id,
            'property_name': property_name or '',
            'property_address': address or '',
            'property_lease_start': lease_start.strftime('%m/%d/%Y') if lease_start else '',
            'property_lease_end': lease_end.strftime('%m/%d/%Y') if lease_end else '',
            'property_rent': str(rent) if rent is not None else '',
            'property_status': status or '',
            'renter_contact': renter_contact or '',
        })
        invitation_link = self.request.build_absolute_uri(f"/register_renter/?{params}")

        send_mail(
            subject="You're invited to join!",
            message=f"Hi {name},\n\nYou've been invited to register for a property! Register here: {invitation_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        messages.success(self.request, "Invitation sent successfully!")
        return super().form_valid(form)