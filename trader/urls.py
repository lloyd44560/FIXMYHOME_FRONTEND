from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView
from trader.views import (
    calendar_events,
    TraderRegistrationCreateView,
    TraderHomeView,
    TraderProfileView,
    TraderEditSecurityView,
    NotificationListView,
    NotificationDetailView,
    MaintenanceListView,
    QuoteListView,
    JobListView,
    BiddingCreateView,
    edit_team_member,
    invite_team_member,
    request_leave,
)

urlpatterns = [
    path('register/', TraderRegistrationCreateView.as_view(), name='register_submit'),
    path('logout-trader/', LogoutView.as_view(next_page=reverse_lazy('login'), http_method_names=['post']), name='logout_trader'),

    # =============== Middleware added: Login Required ===============
    path('home/', TraderHomeView.as_view(), name='home_trader'),
    path("home/calendar/events/", calendar_events, name="calendar_events"),
    path('profile-trader/', TraderProfileView.as_view(), name='profile_trader'),
    path('profile-trader/team-members/edit/<int:member_id>/', edit_team_member, name='edit_team_member'),
    path('profile-trader/team-members/invite/<int:member_id>/', invite_team_member, name='invite_team_member'),
    path("profile-trader/leave/request/", request_leave, name="leave_request"),
    path('profile/security/', TraderEditSecurityView.as_view(), name='trader_edit_security'),
    path("notifications/", NotificationListView.as_view(), name="notification_list"),
    path("notifications/<int:pk>/", NotificationDetailView.as_view(), name="notification_detail"),
    path('maintenance-request/', MaintenanceListView.as_view(), name='maintenance_request_list'),
    path('quote/', QuoteListView.as_view(), name='quote_list'),
    path('jobs/', JobListView.as_view(), name='job_list'),
    path('bidding/create/', BiddingCreateView.as_view(), name='bidding_create'),
    path('chat/', TraderHomeView.trader_chat, name='trader_chat'),
]
