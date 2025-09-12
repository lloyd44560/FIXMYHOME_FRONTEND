from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy

from django.contrib.auth.forms import PasswordChangeForm
from django.views.generic.edit import FormView

# Middleware decorator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from trader.decorators.traderOnly import trader_required

@method_decorator([login_required, trader_required], name='dispatch')
class TraderEditSecurityView(FormView):
    template_name = "components/home/navigatorPages/editSecurityTrader.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy('profile_trader')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # PasswordChangeForm needs user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)  # Keeps session
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))