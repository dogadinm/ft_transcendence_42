from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from .models import User, Score, Room, Friend, ChatGroup
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage


def index(request):
    return render(request, "pong_app/index.html")

def calculator(request):
    return render(request, 'pong_app/calculator.html', {})

def chat_view(request):
    return render(request, 'pong_app/chat.html')

def login_view(request):
    if (request.user.is_authenticated):
        return redirect('index')
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, "pong_app/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "pong_app/login.html")

def register(request):
    if (request.user.is_authenticated):
        return redirect('index')
    if request.method == "POST":

        username = request.POST["username"]
        nickname = request.POST["nickname"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "pong_app/register.html", {
                "message": "Passwords must match."
            })

        if User.objects.filter(username=username).exists():
            return render(request, "pong_app/register.html", {
                "message": "Username already taken."
            })

        if User.objects.filter(nickname=nickname).exists():
            return render(request, "pong_app/register.html", {
                "message": "Nickname already taken."
            })
        # if User.objects.filter(email=email).exists():
        #     return render(request, "pong_app/register.html", {
        #         "message": "Email already taken."
        #     })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            nickname=nickname
        )
        user.save()
        score_entry = Score.objects.create(user=user, score=10)
        score_entry.save()
        friends_list = Friend.objects.create(owner=user)
        friends_list.save()

        login(request, user)
        return redirect('index')
    else:
        return render(request, "pong_app/register.html")


def profile(request, nickname):
    user = User.objects.get(nickname=nickname)
    score = Score.objects.get(user=user)
    is_owner = False
    print(user.nickname)
    if request.user == user:
        is_owner = True



    return render(request, "pong_app/profile.html", {
        "username": user.username,
        "nickname": user.nickname,
        "photo": user.photo.url,
        "score": score.score,
        "user_account": user,
        "is_owner": is_owner,
    })
def logout_view(request):
    logout(request)
    return redirect("index")


@login_required
def profile_settings(request):
    user = request.user

    if request.method == "POST":
        nickname = request.POST.get("nickname")
        description = request.POST.get("description")
        photo = request.FILES.get("photo")

        try:
            user.nickname = nickname
            user.description = description
            if photo:
                user.photo = photo
            user.save()
        except IntegrityError:
            return render(request, "pong_app/profile_settings.html", {
                "message": "Username already taken."
            })



        return redirect("profile_settings")

    return render(request, "pong_app/profile_settings.html", {"user": user})

def add_friend(request):
    return render(request, 'pong_app/add_friend.html')

def pong(request):
    return render(request, 'pong_app/pong.html')

def invite_to_game(request):
    return render(request, 'pong_app/invite_to_game.html')

@login_required(login_url='/login/')
def room(request, room_name):
    return render(request, 'pong_app/room.html', {'room_name': room_name})

def bot(request):
    return render(request, 'pong_app/bot.html')

@login_required(login_url='/login/')
def chat(request, user_id):
    user = User.objects.get(pk=user_id)
    friends_list = Friend.objects.get(owner=user)
    list_f = friends_list.friends.all()


    return render(request, 'pong_app/chat.html', {
        "username": user.username,
        "list_f": list_f,
        "user_account": user,
    })

@login_required(login_url='/login/')
def group_chat(request):
    groups = ChatGroup.objects.all()

    return render(request, 'pong_app/group_chat.html',{
        'groups':groups,
    })

@login_required(login_url='/login/')
def group_chat_name(request, channel_nick):
    return render(request, 'pong_app/group_chat_name.html',{
        'channel_nick':channel_nick,
    })

@login_required(login_url='/login/')
def create_group_chat(request):
    if request.method == "POST":

        username = request.user.username
        group_name = request.POST["group_name"]
        user = User.objects.get(username=username)

        # Attempt to create new user
        try:
            group = ChatGroup.objects.create(owner=user, name=group_name)
            group.save()
        except IntegrityError:
            return render(request, "pong_app/create_group_chat.html", {
                "message": "Group name already taken."
            })
        return redirect('group_chat_name', group_name)
    else:
        return render(request, "pong_app/create_group_chat.html")


