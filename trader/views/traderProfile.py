from django.shortcuts import redirect
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from trader.models import TraderRegistration
from trader.forms import TraderEditProfileForm

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from trader.decorators.traderOnly import trader_required

@method_decorator([login_required, trader_required], name='dispatch')
class TraderProfileView(UpdateView):
    model = TraderRegistration
    form_class = TraderEditProfileForm
    template_name = 'components/home/navigatorPages/viewProfileTrader.html'
    success_url = reverse_lazy('profile_trader')

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
        trader = self.get_object()

        if trader:
            context['full_name'] = user.get_full_name() or trader.name
            context['email'] = user.email or trader.email
            context['phone'] = trader.phone
            context['address'] = trader.address_line_1
            context['addressTwo'] = trader.address_line_2

        else:
            context['error'] = "Trader profile not found."

        return context
    
    def form_valid(self, form):
        objectUpdate = self.get_object()

        # Fields to update
        fields = [
            'name', 'email', 'phone', 'company_type', 'company_name', 'company_address',
            'company_email', 'company_landline', 'abn', 'industry', 'other_expertise', 
            'state', 'municipality', 'city', 'postal_code', 'address_line_1', 'address_line_2',
        ]

        for field in fields:
            setattr(objectUpdate, field, form.cleaned_data[field])

        objectUpdate.save(update_fields=fields)
        return redirect(self.success_url)
    
    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context['error'] = "There was an error updating your profile."
        return self.render_to_response(context)