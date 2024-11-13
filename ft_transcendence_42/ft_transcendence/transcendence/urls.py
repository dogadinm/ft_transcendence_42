from django.contrib import admin
from django.urls import path, re_path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path("login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("account/<int:user_id>", views.account, name="account"),
    re_path(r'pong/', views.pong, name="pong"),
    re_path(r'calculator/', views.calculator, name="calculator"),

    path('<str:room_name>/player1/', views.player1_view, name='player1'),
    path('<str:room_name>/player2/', views.player2_view, name='player2'),
    path('<str:room_name>/spectator/', views.spectator_view, name='spectator'),

]