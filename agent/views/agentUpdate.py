from django.shortcuts import redirect
from django.urls import reverse_lazy

from django.views.generic.edit import UpdateView
from agent.models import AgentRegister
from agent.forms import AgentEditProfileForm

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from agent.decorators.agentOnly import agent_required

@method_decorator([login_required, agent_required], name='dispatch')
class AgentEditProfileView(UpdateView):
    model = AgentRegister
    form_class = AgentEditProfileForm
    template_name = "components/home/navigatorPages/viewProfileAgent.html"
    success_url = reverse_lazy('profile_agent')

    def get_object(self, queryset=None):
        try:
            fetchByRelatedField = self.model.objects.filter(user=self.request.user).first()
            fetchByName = self.model.objects.filter(name=str(self.request.user)).first()
            return fetchByRelatedField or fetchByName

        except self.model.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        agent = self.get_object()

        if agent:
            context['full_name'] = user.get_full_name() or agent.name
            context['email'] = agent.email
            context['phone'] = agent.phone
            context['address'] = agent.address_line_1
            context['addressTwo'] = agent.address_line_2

        else:
            context['error'] = "Agent profile not found."

        return context

    def form_valid(self, form):
        objectUpdate = self.get_object()

        # Fields to update
        fields = [
            'name', 'email', 'phone', 'agency_id', 'website', 'company_name',
            'company_address', 'company_email', 'company_landline',
            'contractor_license', 'service', 'state', 'municipality', 'city',
            'postal_code', 'address_line_1', 'address_line_2'
        ]

        for field in fields:
            setattr(objectUpdate, field, form.cleaned_data[field])

        objectUpdate.save(update_fields=fields)
        return redirect(self.success_url)

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context['error'] = "There was an error updating your profile."
        return self.render_to_response(context)