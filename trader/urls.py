from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView
from trader.views import (
    TraderRegistrationCreateView,
    TraderHomeView,
    TraderProfileView,
    TraderEditSecurityView,
    NotificationListView, 
    NotificationDetailView,
    QuoteListView,
    JobListView,
    BiddingCreateView,
)

urlpatterns = [
    path('register/', TraderRegistrationCreateView.as_view(), name='register_submit'),
    path('logout-trader/', LogoutView.as_view(next_page=reverse_lazy('login'), http_method_names=['post']), name='logout_trader'),

    # =============== Middleware added: Login Required =============== 
    path('home/', TraderHomeView.as_view(), name='home_trader'),
    path('profile-trader/', TraderProfileView.as_view(), name='profile_trader'),
    path('profile/security/', TraderEditSecurityView.as_view(), name='trader_edit_security'),
    path("notifications/", NotificationListView.as_view(), name="notification_list"),
    path("notifications/<int:pk>/", NotificationDetailView.as_view(), name="notification_detail"),
    path('quote/', QuoteListView.as_view(), name='quote_list'),
    path('jobs/', JobListView.as_view(), name='job_list'),
    path('bidding/create/', BiddingCreateView.as_view(), name='bidding_create'),
]
