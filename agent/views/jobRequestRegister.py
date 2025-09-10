from django.contrib import messages
from django.views.generic import CreateView
from django.conf import settings
from django.urls import reverse_lazy
from django.core.mail import send_mail

from trader.models import Jobs
from agent.models import AgentRegister, Property
from agent.forms import AgentCreateJobForm, AgentCreateRoomForm

# Middleware decorator
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from agent.decorators.agentOnly import agent_required

@method_decorator([login_required, agent_required], name='dispatch')
class AgentJobCreateView(CreateView):
    model = Jobs
    form_class = AgentCreateJobForm
    template_name = 'components/home/property_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property_instance = get_object_or_404(Property, pk=self.kwargs['property_id'])
        context['property'] = property_instance
        context['room_form'] = AgentCreateRoomForm()
        context['job_form'] = self.get_form()
        context['jobs'] = Jobs.objects.filter(property=property_instance)
        return context

    def form_valid(self, form):
        agent = AgentRegister.objects.filter(user=self.request.user).first()

        try:
            property_instance = get_object_or_404(Property, pk=self.kwargs['property_id'])
            form.instance.property = property_instance
            form.instance.renter = property_instance.renter or None
            form.instance.agent = agent

            # Access isurgent via related Services (category)
            category = form.cleaned_data.get('category')
            if category and category.isurgent:
                form.instance.priority = True
            else:
                form.instance.priority = False

            # Save the form first to get job_code
            response = super().form_valid(form)

            # Send job creation email to agent
            send_mail(
                subject="Job Created Successfully",
                message=(
                    f"Hi {agent.name},\n\n"
                    f"Your job has been created successfully!\n"
                    f"Job Code: {form.instance.job_code}\n\n"
                    f"Thank you for using FixMyHome."
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[agent.email],
                fail_silently=False,
            )

            messages.success(self.request, f'Job created successfully! Reference: {form.instance.job_code}')
            return response

        except Exception as e:
            messages.error(self.request, f"Error saving job: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error creating the job. Please check the form.")
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        # Ensure reverse_lazy is converted to string
        return str(reverse_lazy('property_view', kwargs={'pk': self.kwargs['property_id']}))