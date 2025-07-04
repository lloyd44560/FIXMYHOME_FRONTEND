from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView
from . import views  # Import your views module

urlpatterns = [
    path('register/', views.AgentRegistrationCreateView.as_view(), name='register_agent'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login'), http_method_names=['post']), name='logout_agent'),

    # =============== Middleware added: Login Required =============== 
    # path('send-invitation-renter/', views.AgentSendInvitation.as_view(), name='renter_invitation'),
    path('home/', views.AgentHomeView.as_view(), name='home_agent'),
    path('profile-agent/', views.AgentEditProfileView.as_view(), name='profile_agent'),
    path('profile/security/', views.AgentEditSecurityView.as_view(), name='agent_edit_security'),

    path('property/create/', views.PropertyCreateView.as_view(), name='property_create'),
    path('property/<int:pk>/edit/', views.PropertyUpdateView.as_view(), name='property_edit'),
    path('property/<int:pk>/delete/', views.delete_property, name='property_delete'),
    path('property/<int:pk>/view/', views.PropertyDetailView.as_view(), name='property_view'),
    path('renters/', views.RenterListView.as_view(), name='manage_renters'),
    path('renters/<int:pk>/edit/', views.RenterUpdateView.as_view(), name='edit_renter'),
    path('agent/jobs/create/', views.AgentJobCreateView.as_view(), name='agent_job_create'),
    path('agent/job-list/', views.JobListView.as_view(), name='job_list_agent'),
    path('bids/', views.AgentBidListView.as_view(), name='agent_bid_list'),
    path('bidding/<int:pk>/approve/', views.BiddingApprovalView.as_view(), name='bidding_approval'),
]
