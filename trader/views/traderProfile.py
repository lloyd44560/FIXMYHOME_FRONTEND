from django.shortcuts import redirect
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from trader.models import TraderRegistration, Leaves, TraderIndustry
from trader.forms import TraderEditProfileForm
from trader.forms import TeamMember

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

        # Fetch all team members linked to this trader
        team_members_qs = TeamMember.objects.filter(trader=trader)
        # Convert queryset to list of dicts (serializable)
        team_members = [
            {
                "id": member.id,
                "name": member.teamName,
                "email": member.email,
                "role": member.position,
                # "date_joined": member.date_joined.strftime("%Y-%m-%d"),
            }
            for member in team_members_qs
        ]

        # Fetch all leave requests for trader's team
        leave_requests_qs = Leaves.objects.filter(team_member__user=user).order_by('-created_at')
        # Convert queryset to list of dicts (safe for JSON)
        leave_requests = [
            {
                "id": leave.id,
                "name": leave.team_member.teamName if leave.team_member else "—",
                "leave_type": leave.leave_type,
                "start_date": leave.start_date.strftime("%Y-%m-%d"),
                "end_date": leave.end_date.strftime("%Y-%m-%d"),
                "reason": leave.reason or "—",
                "status": leave.status or "Pending",
            }
            for leave in leave_requests_qs
        ]

        if trader:
            # Add industries for sidebar
            industries = []
            industries = [
                i.industry.replace("_", " ").title()
                for i in TraderIndustry.objects.filter(trader_id=trader)
            ] if trader else []

            context['full_name'] = user.get_full_name() or trader.name
            context['email'] = user.email or trader.email
            context['phone'] = trader.phone
            context['address'] = trader.address_line_1
            context['addressTwo'] = trader.address_line_2
            context['state'] = trader.state
            context['company_name'] = trader.company_name
            context['abn'] = trader.abn
            context['team_members'] = team_members
            context['is_member'] = trader.isTeamMember
            context['leave_requests'] = leave_requests
            context['industries'] = industries
        else:
            context['error'] = "Trader profile not found."

        return context
    
    def form_valid(self, form):
        trader = self.get_object()
        form.save()

        # ✅ Update industry expertise
        selected = form.cleaned_data.get('industry_expertise', [])
        # Delete old ones not in selected
        TraderIndustry.objects.filter(trader=trader).exclude(industry__in=selected).delete()
        # Add new ones
        for exp in selected:
            TraderIndustry.objects.get_or_create(trader=trader, industry=exp)

        return redirect(self.success_url)
    
    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        context['error'] = "There was an error updating your profile."
        return self.render_to_response(context)