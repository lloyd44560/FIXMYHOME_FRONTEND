from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView
from . import views  # Import your views module

urlpatterns = [
    path('register/', views.TraderRegistrationCreateView.as_view(), name='register_submit'),
    path('logout-trader/', LogoutView.as_view(next_page=reverse_lazy('login'), http_method_names=['post']), name='logout_trader'),

    # =============== Middleware added: Login Required =============== 
    path('home/', views.TraderHomeView.as_view(), name='home_trader'),
    path('profile-trader/', views.TraderProfileView.as_view(), name='profile_trader'),
    path('profile/security/', views.TraderEditSecurityView.as_view(), name='trader_edit_security'),
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('bidding/create/', views.BiddingCreateView.as_view(), name='bidding_create'),
]
