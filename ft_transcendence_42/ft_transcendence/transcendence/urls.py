from django.contrib import admin
from django.urls import path, re_path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path("login/", views.login_view, name='login'),
    path("logout", views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('chat/<int:user_id>', views.chat, name='chat'),
    path('account/<int:user_id>', views.account, name='account'),
    path('room/<str:room_name>/', views.room, name='room'),
    path("bot/", views.bot, name='bot'),
    path('group_chat/', views.group_chat, name='group_chat'),
    path('group_chat/<str:channel_nick>', views.group_chat_name, name='group_chat_name'),
    path('create_group_chat/', views.create_group_chat, name='create_group_chat'),
    re_path(r'pong/', views.pong, name="pong"),
]