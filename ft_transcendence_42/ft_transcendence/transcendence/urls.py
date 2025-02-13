from django.urls import path
from . import views

urlpatterns = [
    #Main Page
    path('', views.index, name='index'),
    path('user-links/', views.user_links, name='user_links'),

    #Login, Logout, Register
    path('login/', views.login_view, name='login'),
    path("logout/", views.logout_view, name='logout'),
    path('login/42/', views.login_with_42, name='login_with_42'),
    path('callback/', views.callback, name='callback'),
    path('register/', views.register, name='register'),

    #Chat
    path('chat/', views.chat, name='chat'),
    path('invite_to_game/', views.invite_to_game, name='invite_to_game'),

    #Find
    path('find_lobby/', views.find_lobby, name="find_lobby"),
    path('find_tournament/', views.find_tournament, name='find_tournament'),
    path("find_friend/", views.find_friend, name='find_friend'),
    path('find_doublejack/', views.find_doublejack, name='find_doublejack'),

    #User
    path('profile/<str:username>', views.profile, name='profile'),
    path('profile_settings/', views.profile_settings, name='profile_settings'),
    path('friend_requests/', views.friend_requests, name='friend_requests'),
    path("blockedPeople/", views.blocked_people, name='blockedPeople'),
    path('full_match_history/<str:username>', views.full_match_history, name='full_match_history'),
    path('full_friends_list/<str:username>', views.full_friends_list, name='full_friends_list'),   

    #Games
	path("bot/", views.bot, name='bot'),
    path("pong_lobby/<str:room_lobby>/", views.pong_lobby, name='pong_lobby'),
    path('tournament/<str:tournament_id>/', views.tournament, name='tournament'),
    path("doublejack_lobby/<str:room_lobby>/", views.doublejack, name='doublejack_lobby'),
]