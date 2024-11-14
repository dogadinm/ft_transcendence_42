from django.contrib import admin
from django.urls import path, re_path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path("login/", views.login_view, name='login'),
    path("logout", views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('chat/', views.chat, name='chat'),
    path('account/<int:user_id>', views.account, name='account'),
    path('room/<str:room_name>/', views.room, name='room'),
    path("bot/", views.bot, name='bot'),
    re_path(r'pong/', views.pong, name="pong"),
]