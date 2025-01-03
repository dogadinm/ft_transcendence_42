#
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from .models import User, Score, Room, Friend, ChatGroup, FriendRequest, MatchHistory
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator



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

def find_fiend(request):
    if request.method == "POST":
        username = request.POST.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                return redirect('profile', username=user.username)
            except User.DoesNotExist:
                messages.error(request, f"User {username} doesn't exist.")
                return redirect('profile', username=request.user.username)
        else:
            messages.error(request, "Enter username")
            return redirect('profile', username=request.user.username)

    return redirect('index')

def profile(request, username):
    page_user = get_object_or_404(User, username=username)
    main_user = request.user
    score = Score.objects.get(user=page_user)
    recent_matches = MatchHistory.objects.filter(
        Q(winner=page_user) | Q(loser=page_user)
    ).order_by('-created_at')[:3]

    main_user_friends = Friend.objects.get(owner=main_user)
    page_user_friends = Friend.objects.get(owner=page_user)
    list_m = main_user_friends.friends.all()[:3]
    list_p = page_user_friends.friends.all()[:3]
    block_list = main_user.blocked_users.all()

    if request.method == "POST":
        action = request.POST.get('action')
        if (request.POST.get('sender_request')):
            sender_request = User.objects.get(username=request.POST.get('sender_request'))
            sender_request_friends = Friend.objects.get(owner=sender_request)

        if action == 'send_request':
            if not (page_user in main_user_friends.friends.all() and FriendRequest.objects.filter(sender=main_user, receiver=page_user).exists()):
                FriendRequest.objects.create(sender=main_user, receiver=page_user)
        elif action == 'delete':
            main_user_friends.friends.remove(page_user)
            main_user_friends.save()
            page_user_friends.friends.remove(main_user)
            page_user_friends.save()
        elif action == 'accept_request':
            friend_request = FriendRequest.objects.filter(sender=sender_request, receiver=main_user).first()
            if friend_request:
                main_user_friends.friends.add(sender_request)
                sender_request_friends.friends.add(main_user)
                friend_request.delete()
        elif action == 'decline_request':
            friend_request = FriendRequest.objects.filter(sender=sender_request, receiver=main_user).first()
            if friend_request:
                friend_request.delete()
        elif action == 'block_user':
            main_user.blocked_users.add(page_user)
            main_user.save()
        elif action == 'unblock_user':
            main_user.blocked_users.remove(page_user)
            main_user.save()

        return redirect("profile", username=username)

    friend_request_sent = FriendRequest.objects.filter(sender=main_user, receiver=page_user).exists()
    friend_request_taker = FriendRequest.objects.filter(sender=page_user, receiver=main_user).exists()
    friend_requests = FriendRequest.objects.filter(receiver=page_user)


    return render(request, "pong_app/profile.html", {
        "username": page_user.username,
        "nickname": page_user.nickname,
        "description": page_user.description,
        "photo": page_user.photo.url,
        "score": score.score,
        "user_account": page_user,
        "is_owner": request.user == page_user,
        "list_m": list_m,
        "list_p": list_p,
        "friend": page_user in main_user_friends.friends.all(),
        "block_user": page_user in main_user.blocked_users.all(),
        "friend_request_sent": friend_request_sent,
        "friend_request_taker":friend_request_taker,
        "friend_requests": friend_requests,
        "block_list":block_list,
        "recent_matches":recent_matches,
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



def bot(request):
    return render(request, 'pong_app/bot.html')

@login_required(login_url='/login/')
def chat(request):
    groups = ChatGroup.objects.filter(Q(owner=request.user) | Q(members=request.user))
    friends = Friend.objects.get(owner=request.user)

    return render(request, 'pong_app/chat.html', {
        "friends": friends.friends.all(),
        "current_user": request.user.username,
        "groups":groups,
    })

def doublejack(request):
    return render(request, 'pong_app/doublejack.html')

def get_friend_requests_count(request):
    if request.user.is_authenticated:
        count = FriendRequest.objects.filter(receiver=request.user).count()
        return JsonResponse({"count": count})
    return JsonResponse({"count": 0})


def full_match_history(request, username):
    user = get_object_or_404(User, username=username)

    matches = MatchHistory.objects.filter(
        Q(winner=user) | Q(loser=user)
    ).order_by('-created_at')

    paginator = Paginator(matches, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pong_app/full_match_history.html', {'page_obj': page_obj, 'username': user.username})

def full_friends_list(request, username):
    user = get_object_or_404(User, username=username)
    friend_objct = get_object_or_404(Friend, owner=user)
    friends = friend_objct.friends.all()

    paginator = Paginator(friends, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pong_app/full_friends_list.html', {
        'page_obj': page_obj,
        'username': user.username
    })


@login_required(login_url='/login/')
def pong_lobby(request, room_lobby):
    user = request.user
    admin_user = get_object_or_404(User, username="admin")
    group, created = ChatGroup.objects.get_or_create(owner = admin_user, name=room_lobby)
    group.save()


    if created:
        group.owner = admin_user
        group.save()

    group.members.add(user)
    group.save()

    return render(request, 'pong_app/pong_lobby.html', {'room_lobby': room_lobby})

