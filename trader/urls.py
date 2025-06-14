from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views  # Import your views module

urlpatterns = [
    path('home/', views.TraderHomeView.as_view(), name='home_trader'),
    path('register/', views.TraderRegistrationCreateView.as_view(), name='register_submit'),
    path('logout-trader/', LogoutView.as_view(next_page='/login/'), name='logout_trader'),
]
