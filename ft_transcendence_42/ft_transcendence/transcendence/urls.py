from django.contrib import admin
from django.urls import path, re_path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path("logout/", views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
	# path("bind_wallet/", views.bind_wallet, name="bind_wallet"),

    path('chat/', views.chat, name='chat'),
	path('tournament/<str:tournament_id>/', views.tournament, name='tournament'),
	path('find_tournament/', views.find_tournament, name='find_tournament'),

    path('profile/<str:username>', views.profile, name='profile'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),
    path("blockedPeople/", views.blocked_people, name='blockedPeople'),

    path('full_match_history/<str:username>', views.full_match_history, name='full_match_history'),
    path('full_friends_list/<str:username>', views.full_friends_list, name='full_friends_list'),   

    path("bot/", views.bot, name='bot'),
	path("doublejack_lobby/<str:room_lobby>/", views.doublejack, name='doublejack_lobby'),
	path('find_doublejack/', views.find_doublejack, name='find_doublejack'),
	
    path("pong_lobby/<str:room_lobby>/", views.pong_lobby, name='pong_lobby'),

    path("find_friend/", views.find_friend, name='find_friend'),
    path('invite_to_game/', views.invite_to_game, name='invite_to_game'),

    re_path(r'find_lobby/', views.find_lobby, name="find_lobby"),
    path('login/42/', views.login_with_42, name='login_with_42'),
    path('callback/', views.callback, name='callback'),
    path('user-links/', views.user_links, name='user_links'),
    path('friend_requests/', views.friend_requests, name='friend_requests'),
]