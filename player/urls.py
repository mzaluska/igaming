from django.urls import path, re_path
from django.contrib.auth.views import LogoutView, LoginView
from . import views

urlpatterns = [
    path('home/', views.home, name='player_home'),
    path('home/', views.home, name='player_home_spin'),
    path('login', LoginView.as_view(template_name="player/login_form.html"), name="player_login"),
    path('logout', LogoutView.as_view(), name="player_logout"),
    path('signup', views.SignUpView.as_view(), name='player_signup'),
    path('deposit/', views.deposit_money, name='player_deposit'),
]