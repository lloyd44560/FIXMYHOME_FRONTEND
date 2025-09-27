from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.timezone import now

from django.urls import reverse_lazy,reverse

from django.core.paginator import Paginator
from django.views.generic import TemplateView
from trader.models import Jobs
from agent.models import AgentRegister, Property
from renter.models import RequestReport
from agent.forms import RespondRequestForm

# Middleware decorator
from agent.decorators.agentOnly import agent_required

from django.core.mail import EmailMessage
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages


# View for the home page
@method_decorator([login_required, agent_required], name='dispatch')
class AgentHomeView(TemplateView):
    template_name = 'pages/homeAgent.html'
    success_url = reverse_lazy("home_agent")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get only active properties
        properties_list = Property.objects.filter(is_active=True).order_by('-created_at')

        # Set up pagination
        paginator = Paginator(properties_list, 10)  # Show 10 properties per page
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['properties'] = page_obj
        context['page_obj'] = page_obj  # For pagination controls

        agent = AgentRegister.objects.get(user=self.request.user)

        # Count by status & priority
        context['to_quote_urgent'] = Jobs.objects.filter(agent=agent, status='quoted', priority=True).count()
        context['to_quote_non_urgent'] = Jobs.objects.filter(agent=agent, status='quoted', priority=False).count()

        context['pending_urgent'] = Jobs.objects.filter(agent=agent, status='confirmed', priority=True).count()
        context['pending_non_urgent'] = Jobs.objects.filter(agent=agent, status='confirmed', priority=False).count()

        context['approved_urgent'] = Jobs.objects.filter(agent=agent, status='approved', priority=True).count()
        context['approved_non_urgent'] = Jobs.objects.filter(agent=agent, status='approved', priority=False).count()

        # Jobs Today (scheduled today)
        today = now().date()
        context['today_urgent'] = Jobs.objects.filter(agent=agent, scheduled_at__date=today, priority=True).count()
        context['today_non_urgent'] = Jobs.objects.filter(agent=agent, scheduled_at__date=today, priority=False).count()

        # Add renter requests for this agent
        context['renter_requests'] = RequestReport.objects.filter(agent=agent).order_by('-date_requested')
        context['respond_form'] = RespondRequestForm()

        return context

    def post(self, request, *args, **kwargs):
        request_id = request.POST.get("request_id")
        subject = request.POST.get("subject")
        message_text = request.POST.get("message")
        attachment = request.FILES.get("attachment")

        # Get renter & agent
        from renter.models import RequestReport
        req = RequestReport.objects.get(id=request_id)
        renter_email = req.renter.user.email  # assuming renter has a linked user with email
        agent_email = request.user.email

        # Build email
        email = EmailMessage(
            subject=subject,
            body=message_text,
            from_email=agent_email,
            to=[renter_email],
        )

        # Attach file if present
        if attachment:
            email.attach(attachment.name, attachment.read(), attachment.content_type)

        # Send it
        email.send()

        # Optionally update status
        req.status = "in_progress"
        req.save()

        # Add success message
        messages.success(request, f"Response successfully sent to {req.renter}")

        # Redirect to GET so the message shows
        from django.shortcuts import redirect
        return redirect("home_agent")


