from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy

from django.views.generic import TemplateView, CreateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User

from .models import AgentRegister
from .forms import CreateAgentFormClass, AgentEditProfileForm

# Create your views here.
class AgentRegistrationCreateView(CreateView):
    model = AgentRegister
    form_class = CreateAgentFormClass
    template_name = 'pages/registerAgent.html'
    success_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            # Duplicate username or email check
            username = form.cleaned_data['name']
            email = form.cleaned_data['email']

            if User.objects.filter(username=username).exists():
                form.add_error('name', 'Username already exists.')
            if User.objects.filter(email=email).exists():
                form.add_error('email', 'Email already exists.')

            if form.errors:
                # Return with form errors due to duplicates
                return render(request, self.template_name, {'form': form})
            
            agent = form.save(commit=False)
            user = User.objects.create_user(
                username=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                is_superuser=1
            )
            agent.user = user
            agent.password = None
            agent.save()

            return redirect(self.success_url)
        else:
            return render(request, self.template_name, {'form': form})

# View for the home page
@method_decorator(login_required, name='dispatch')
class AgentHomeView(TemplateView):
    template_name = 'pages/homeAgent.html'

@method_decorator(login_required, name='dispatch')
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

        else:
            context['error'] = "Agent profile not found."

        return context

    def form_valid(self, form):
        objectUpdate = self.get_object()

        # Fields to update
        fields = [
            'name', 'email', 'phone', 'agency_id', 'website', 'notes', 'password',
            'company_name', 'company_address', 'company_email', 'company_landline',
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
