from django.contrib import admin
from django.urls import path, re_path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path("login/", views.login_view, name='login'),
    path("logout", views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    path('chat/', views.chat, name='chat'),
    path('group_chat/', views.group_chat, name='group_chat'),
    path('group_chat/<str:channel_nick>', views.group_chat_name, name='group_chat_name'),
    path('create_group_chat/', views.create_group_chat, name='create_group_chat'),

    path('profile/<str:username>', views.profile, name='profile'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),

    path('full_match_history/<str:username>', views.full_match_history, name='full_match_history'),
    path('full_friends_list/<str:username>', views.full_friends_list, name='full_friends_list'),   

    path('room/<str:room_name>/', views.room, name='room'),
    path("bot/", views.bot, name='bot'),
	path("doublejack/", views.doublejack, name='doublejack'),
    path("pong_loby/<str:room_loby>/", views.pong_loby, name='pong_loby'),


    path('api/friend_requests_count/', views.get_friend_requests_count, name='friend_requests_count'),
    path('invite_to_game/', views.invite_to_game, name='invite_to_game'),


    re_path(r'pong/', views.pong, name="pong"),
]