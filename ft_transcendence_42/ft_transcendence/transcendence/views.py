import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.conf import settings
from .models import User, Score, Room, Friend, ChatGroup, FriendRequest, MatchHistory
from .forms import ProfileSettingsForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse



def index(request):
    if request.user.is_authenticated:
        return render(request, "pong_app/index.html", {"user_links_template": "pong_app/user_links_authenticated.html"})
    else:
        return render(request, "pong_app/index.html", {"user_links_template": "pong_app/user_links_guest.html"})


def user_links(request):
    if request.user.is_authenticated:
        return render(request, "pong_app/user_links_authenticated.html")
    return render(request, "pong_app/user_links_guest.html")


def login_view(request):
    if request.user.is_authenticated:
        return render(request, "pong_app/index.html")
        # return JsonResponse({"success": True, "redirect": "/"}, status=200)

    if request.method == "POST":
        # Parse data from the POST request
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "redirect": "/"}, status=200)
            # return render(request, "pong_app/index.html", {"user_links_template": "pong_app/user_links_authenticated.html"})
        else:
            return JsonResponse({"success": False, "error": "Invalid username and/or password."}, status=400)
    elif request.method == "GET":
        return render(request, "pong_app/login.html")

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)

    response = redirect('index')
    response.delete_cookie(settings.SESSION_COOKIE_NAME)

    # Clear any other authentication cookies if you have them
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path='/')
    return JsonResponse({"success": True, "redirect": "/"}, status=200)


def register(request):
    if (request.user.is_authenticated):
        return render(request, "pong_app/index.html")
    if request.method == "POST":
        username = request.POST.get("username")
        nickname = request.POST.get("nickname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")

        if password != confirmation:
            return JsonResponse({"error": "Passwords must match."}, status=400)

        if len(password) < 8:
            return JsonResponse({"error": "Password must be at least 8 characters long."}, status=400)
        if not any(char.isupper() for char in password):
            return JsonResponse({"error": "Password must contain at least one uppercase letter."}, status=400)
        if not any(char.isdigit() for char in password):
            return JsonResponse({"error": "Password must contain at least one digit."}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already taken."}, status=400)

        if User.objects.filter(nickname=nickname).exists():
            return JsonResponse({"error": "Nickname already taken."}, status=400)

        user = User.objects.create_user(username=username, password=password, nickname=nickname)
        user.save()

        Score.objects.create(user=user, score=10)
        Friend.objects.create(owner=user)

        login(request, user)
        return JsonResponse({"redirect": "/"})
    elif request.method == "GET":
        return render(request, "pong_app/register.html")

    return JsonResponse({"error": "Invalid request method."}, status=405)




@login_required(login_url='/login/')
def profile(request, username):
    page_user = get_object_or_404(User, username=username)
    main_user = request.user
    score = Score.objects.get(user=page_user)

    main_user_friends = Friend.objects.get(owner=main_user)
    page_user_friends = Friend.objects.get(owner=page_user)

    block_list = main_user.blocked_users.all()

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        action = request.POST.get('action')
        response_data = {"success": False}

        if request.POST.get('sender_request'):
            sender_request = User.objects.get(username=request.POST.get('sender_request'))
            sender_request_friends = Friend.objects.get(owner=sender_request)

        if action == 'send_request':
            if not FriendRequest.objects.filter(sender=main_user, receiver=page_user).exists():
                FriendRequest.objects.create(sender=main_user, receiver=page_user)
                return JsonResponse({"success": True, "redirect": f"/profile/{username}"}, status=200)

        elif action == 'delete':
            main_user_friends.friends.remove(page_user)
            main_user_friends.save()
            page_user_friends.friends.remove(main_user)
            page_user_friends.save()
            return JsonResponse({"success": True, "redirect": f"/profile/{username}"}, status=200)

        elif action == 'block_user':
            main_user.blocked_users.add(page_user)
            main_user.save()
            return JsonResponse({"success": True, "redirect": f"/profile/{username}"}, status=200)
        elif action == 'unblock_user':
            main_user.blocked_users.remove(page_user)
            main_user.save()
            return JsonResponse({"success": True, "redirect": f"/profile/{username}"}, status=200)


        response_data["html"] = render_to_string("pong_app/profile.html", {
            "friend": page_user in main_user_friends.friends.all(),
            "friend_request_sent": FriendRequest.objects.filter(sender=main_user, receiver=page_user).exists(),
            "friend_request_taker": FriendRequest.objects.filter(sender=page_user, receiver=main_user).exists(),
            "block_user": page_user in main_user.blocked_users.all(),
            "is_owner": request.user == page_user,
            "username": page_user.username,
        }, request=request)

        return JsonResponse(response_data)

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

        "friend": page_user in main_user_friends.friends.all(),
        "block_user": page_user in main_user.blocked_users.all(),
        "friend_request_sent": friend_request_sent,
        "friend_request_taker": friend_request_taker,
        "friend_requests": friend_requests,
        "block_list": block_list,

    })


@login_required(login_url='/login/')
def friend_requests(request):
    main_user = request.user

    if request.method == "GET":
        friend_requests = FriendRequest.objects.filter(receiver=main_user)
        return render(request, "pong_app/friend_requests.html", {"friend_requests": friend_requests})

    elif request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        action = request.POST.get('action')
        sender_request = User.objects.filter(username=request.POST.get('sender_request')).first()
        main_user_friends = Friend.objects.get(owner=main_user)
        sender_request_friends = Friend.objects.get(owner=sender_request)
        response_data = {"success": False}

        if not sender_request:
            return JsonResponse({"success": False, "message": "User not found."})

        if action == 'accept_request':
            friend_request = FriendRequest.objects.filter(sender=sender_request, receiver=main_user).first()
            if friend_request:
                main_user_friends.friends.add(sender_request)
                sender_request_friends.friends.add(main_user)
                friend_request.delete()
                response_data["success"] = True
                response_data["message"] = "Friend request accepted."

        elif action == 'decline_request':
            friend_request = FriendRequest.objects.filter(sender=sender_request, receiver=main_user).first()
            if friend_request:
                friend_request.delete()
                response_data["success"] = True
                response_data["message"] = "Friend request declined."

        return JsonResponse(response_data)

@login_required
def profile_settings(request):
    user = request.user

    if request.method == "POST":
        form = ProfileSettingsForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            user.nickname = form.cleaned_data["nickname"]
            user.description = form.cleaned_data["description"]
            if form.cleaned_data["photo"]:
                user.photo = form.cleaned_data["photo"]
            user.save()

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "message": "Settings updated successfully.",
                    "updated_fields": {
                        "nickname": user.nickname,
                        "description": user.description,
                    }
                })

        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": False,
                    "message": "Validation failed.",
                    "errors": form.errors,
                }, status=400)

    else:
        form = ProfileSettingsForm(initial={
            "nickname": user.nickname,
            "description": user.description,
        })

    return render(request, "pong_app/profile_settings.html", {"form": form, "user": user})


@login_required(login_url='/login/')
def add_friend(request):
    return render(request, 'pong_app/add_friend.html')

@login_required(login_url='/login/')
def pong(request):
    return render(request, 'pong_app/pong.html')

@login_required(login_url='/login/')
def invite_to_game(request):
    return render(request, 'pong_app/invite_to_game.html')


@login_required(login_url='/login/')
def bot(request):
    return render(request, 'pong_app/bot.html')

@login_required(login_url='/login/')
def chat(request):
    groups = ChatGroup.objects.filter(members=request.user)
    friend_obj = Friend.objects.get(owner=request.user)

    return render(request, 'pong_app/chat.html', {
        "friends": friend_obj.friends.all(),
        "current_user": request.user.username,
        "groups": groups,
    })


@login_required(login_url='/login/')
def doublejack(request):
    return render(request, 'pong_app/doublejack.html')

@login_required(login_url='/login/')
def get_friend_requests_count(request):
    if request.user.is_authenticated:
        count = FriendRequest.objects.filter(receiver=request.user).count()
        return JsonResponse({"count": count})
    return JsonResponse({"count": 0})

@login_required(login_url='/login/')
def full_match_history(request, username):
    user = get_object_or_404(User, username=username)
    friend_objct = get_object_or_404(Friend, owner=user)
    matches = MatchHistory.objects.filter(
        Q(winner=user) | Q(loser=user)
    ).order_by('-created_at')

    paginator = Paginator(matches, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pong_app/full_match_history.html', {
        'page_obj': page_obj,
        'username': user.username,
        "is_owner": request.user.username == username,
        "friend": request.user in friend_objct.friends.all(),
    })

@login_required(login_url='/login/')
def full_friends_list(request, username):
    user = get_object_or_404(User, username=username)
    friend_objct = get_object_or_404(Friend, owner=user)
    friends = friend_objct.friends.all()

    paginator = Paginator(friends, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    return render(request, "pong_app/full_friends_list.html", {
        "page_obj": page_obj,
        "username": user.username,
        "is_owner": request.user.username == username,
        "friend": request.user in friend_objct.friends.all(),
    })

@login_required(login_url='/login/')
def blocked_people(request):
    main_user = request.user

    if request.method == "GET":
        block_list = main_user.blocked_users.all()
        return render(request, "pong_app/blockedPeople.html", {"block_list": block_list})
    return JsonResponse("Error")


@login_required(login_url='/login/')
def pong_lobby(request, room_lobby):
    user = request.user
    username = user.username
    admin_user = get_object_or_404(User, username=username)
    group, created = ChatGroup.objects.get_or_create(name=room_lobby)
    group.save()

    if created:
        group.owner = admin_user
        group.save()

    # group.members.add(user)
    # group.save()
    return render(request, 'pong_app/pong_lobby.html', {'room_lobby': room_lobby})



def login_with_42(request):
    authorize_url = f"{settings.FT_API_AUTHORIZE_URL}?client_id={settings.FT_API_CLIENT_ID}&redirect_uri={settings.FT_API_REDIRECT_URI}&response_type=code"
    return redirect(authorize_url)

def callback(request):
    # Retrieve the authorization code from the request
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'error': 'Authorization code not provided'}, status=400)

    try:
        # Step 1: Exchange the authorization code for an access token
        token_response = requests.post(settings.FT_API_TOKEN_URL, data={
            'grant_type': 'authorization_code',
            'client_id': settings.FT_API_CLIENT_ID,
            'client_secret': settings.FT_API_CLIENT_SECRET,
            'code': code,
            'redirect_uri': settings.FT_API_REDIRECT_URI,
        })
        token_response.raise_for_status()  # Raise an exception for HTTP errors

        token_data = token_response.json()
        access_token = token_data.get('access_token')
        if not access_token:
            return JsonResponse({'error': 'Access token not provided in response'}, status=400)

        # Step 2: Fetch user information using the access token
        user_info_response = requests.get(f"{settings.FT_API_BASE_URL}/v2/me", headers={
            'Authorization': f'Bearer {access_token}'
        })
        user_info_response.raise_for_status()  # Raise an exception for HTTP errors

        user_data = user_info_response.json()

        # Step 3: Create or get the user in the database
        user, created = User.objects.get_or_create(
            username=user_data['login'],
            nickname= user_data['first_name'] + ' ' + user_data['last_name'],
            email=user_data['email'],
        )


        if created:
            # If the user was created, set an unusable password and save related objects
            user.set_unusable_password()
            user.save()

            # Create related objects such as Score and Friend
            Score.objects.create(user=user, score=10)
            Friend.objects.create(owner=user)

        # Step 4: Log the user in
        login(request, user)

        # Redirect the user to the homepage
        return redirect('index')

    except requests.exceptions.RequestException as e:
        # Handle HTTP request errors
        return JsonResponse({'error': 'Failed to communicate with 42 API', 'details': str(e)}, status=500)

    except IntegrityError as e:
        # Handle database integrity errors (e.g., unique constraint violations)
        return JsonResponse({'error': 'Database integrity error', 'details': str(e)}, status=500)

    except Exception as e:
        # Handle unexpected errors
        return JsonResponse({'error': 'An unexpected error occurred', 'details': str(e)}, status=500)
