from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView
from . import views  # Import your views module

urlpatterns = [
    path('register/', views.AgentRegistrationCreateView.as_view(), name='register_agent'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('login'), http_method_names=['post']), name='logout_agent'),

    # =============== Middleware added: Login Required =============== 
    path('home/', views.AgentHomeView.as_view(), name='home_agent'),
    path('view-profile/', views.AgentProfileView.as_view(), name='profile_agent'),
]
