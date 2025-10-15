from django.conf.urls.static import static
from django.urls import path, reverse_lazy
from django.conf import settings

from django.contrib.auth.views import LogoutView

from agent.views import (
    AgentRegistrationCreateView, AgentHomeView, AgentEditProfileView,
    AgentEditSecurityView, PropertyCreateView, PropertyUpdateView,
    delete_property, archive_property, get_bidding, PropertyDetailView, PropertiesListView,
    RoomCreateView, InviteRenterView, RenterListView, RenterUpdateView,
    AgentJobCreateView, ActiveJobsListView, AgentBidListView, BiddingApprovalView
)

urlpatterns = [
    path('register/', AgentRegistrationCreateView.as_view(), name='register_agent'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login'), http_method_names=['post']), name='logout_agent'),

    # =============== Middleware added: Login Required ===============
    # path('send-invitation-renter/', views.AgentSendInvitation.as_view(), name='renter_invitation'),
    path('home/', AgentHomeView.as_view(), name='home_agent'),
    path('profile-agent/', AgentEditProfileView.as_view(), name='profile_agent'),
    path('profile/security/', AgentEditSecurityView.as_view(), name='agent_edit_security'),
    path("active-jobs/get-bidding/<int:job_id>/", get_bidding, name="get_bidding"),

    path('property/create/', PropertyCreateView.as_view(), name='property_create'),
    path('property/<int:pk>/edit/', PropertyUpdateView.as_view(), name='property_edit'),
    path('property/<int:pk>/delete/', delete_property, name='property_delete'),
    path('property/<int:pk>/archive/', archive_property, name='property_archive'),
    path('property/<int:pk>/view/', PropertyDetailView.as_view(), name='property_view'),
    path('properties/', PropertiesListView.as_view(), name='manage_properties'),
    path('property/<int:property_id>/room/create/', RoomCreateView.as_view(), name='create_room'),

    path('renter-invitation/', InviteRenterView.as_view(), name='renter_invitation'),
    path('renters/', RenterListView.as_view(), name='manage_renters'),
    path('renters/<int:pk>/edit/', RenterUpdateView.as_view(), name='edit_renter'),

    path('jobs/create/<int:property_id>/', AgentJobCreateView.as_view(), name='agent_job_create'),
    path('active-jobs/', ActiveJobsListView.as_view(), name='active_jobs_list'),

    path('bids/', AgentBidListView.as_view(), name='agent_bid_list'),
    path('bidding/<int:pk>/approve/', BiddingApprovalView.as_view(), name='bidding_approval'),
    path('chat/', AgentHomeView.agent_chat, name='agent_chat'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
