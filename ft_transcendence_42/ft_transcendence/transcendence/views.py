import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.conf import settings
from .models import User, Score, Friend, FriendRequest, MatchHistory, ScoreDoubleJack
from .forms import ProfileSettingsForm, LoginForm, RegistrationForm, FiendFriendForm, FiendLobbyForm, FiendTournamentForm, FindDoublejackForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse
import json
import os
from . import blockchain
from .TournamentGame import tournament_manager

# Main Page
def index(request):
    if request.user.is_authenticated:
        return render(request, "pong_app/index.html", {"user_links_template": "pong_app/user_links_authenticated.html"})
    else:
        return render(request, "pong_app/index.html", {"user_links_template": "pong_app/user_links_guest.html"})


def user_links(request):
    if request.user.is_authenticated:
        return render(request, "pong_app/user_links_authenticated.html")
    return render(request, "pong_app/user_links_guest.html")





# Login, Logout
def login_view(request):
    if request.user.is_authenticated:
        return render(request, "pong_app/index.html")
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                return JsonResponse({"success": True, "redirect": "/"}, status=200)
            else:
                return JsonResponse({"success": False, "error": "Invalid username and/or password."}, status=400)
        else:
            errors = form.errors.as_json()
            return JsonResponse({"success": False, "error": errors}, status=400)
    elif request.method == "GET":
        return render(request, "pong_app/login.html")

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

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
            email=user_data['email'],
            tournament_nickname = user_data['login'],
        )

        if created:
            # If the user was created, set an unusable password and save related objects
            user.set_unusable_password()
            user.wallet_address, user.wallet_prt_key = bind_walet()
            user.save()

            # Create related objects such as Score and Friend
            Score.objects.create(user=user, score=10)
            Friend.objects.create(owner=user)
            ScoreDoubleJack.objects.create(user=user, score=1000)

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
def remove_first_two_lines(wallet_file_path):
    with open(wallet_file_path, 'r') as file:
        lines = file.readlines()
    
    if len(lines) > 2:
        with open(wallet_file_path, 'w') as file:
            file.writelines(lines[2:])

@login_required(login_url='/login/')
def logout_view(request):
    response = JsonResponse({"success": True, "redirect": "/"}, status=200)
    for cookie in request.COOKIES:
        response.delete_cookie(cookie)

    logout(request)
    return response





# Registration
def bind_walet():
    wallet_file_path = os.path.join(os.path.dirname(__file__), 'wallet.txt')
    
    with open(wallet_file_path, 'r') as file:
        lines = file.readlines()
        
        if len(lines) <= 1:  # Check if the file doesn't contain enough lines
            return False, False
        
        # Extract wallet address and private key
        wallet_address = lines[0].strip()  # First line as wallet address
        wallet_prt_key = lines[1].strip()  # Second line as private key
        
        # Remove the first two lines
        lines = lines[2:]

    # Rewrite the file with the remaining lines
    with open(wallet_file_path, 'w') as file:
        file.writelines(lines)
        
    return wallet_address, wallet_prt_key

def register(request):
    if request.user.is_authenticated:
        return render(request, "pong_app/index.html")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            wallet_address, wallet_prt_key = bind_walet()
            if not wallet_address:
                return JsonResponse({"wallet_error":  "No wallet addresses found. Please wait!"}, status=400)
            # Create the user and other related objects
            user = User.objects.create_user(username=username, password=password, email=email)


            user.wallet_address = wallet_address
            user.wallet_prt_key = wallet_prt_key
            user.tournament_nickname = username
            user.save()
            Score.objects.create(user=user, score=10)
            ScoreDoubleJack.objects.create(user=user, score=1000)
            Friend.objects.create(owner=user)
            login(request, user)
            return JsonResponse({"redirect": "/"})
        else:
            print(form.errors)
            return JsonResponse({"error": form.errors}, status=400)

    elif request.method == "GET":
        form = RegistrationForm()

    return render(request, "pong_app/register.html", {"form": form})





# User Manager
@login_required(login_url='/login/')
def profile(request, username):
    page_user = get_object_or_404(User, username=username)
    main_user = request.user
    score = Score.objects.get(user=page_user)
    score_double_jack = ScoreDoubleJack.objects.get(user=page_user)

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
        "description": page_user.description,
        "photo": page_user.photo.url,
        "score": score.score,
        "score_double_jack": score_double_jack.score,
        "user_account": page_user,
        "is_owner": request.user == page_user,

        "friend": page_user in main_user_friends.friends.all(),
        "block_user": page_user in main_user.blocked_users.all(),
        "friend_request_sent": friend_request_sent,
        "friend_request_taker": friend_request_taker,
        "friend_requests": friend_requests,
        "block_list": block_list,
		"wallet":page_user.wallet_address,

    })



@login_required
def profile_settings(request):
    user = request.user

    if request.method == "POST":
        form = ProfileSettingsForm(request.POST, request.FILES, user=user)
        print(form)
        print(form.is_valid())
        if form.is_valid():
            user.tournament_nickname = form.cleaned_data["tournament_nickname"]
            user.description = form.cleaned_data["description"]
            if "photo" in request.FILES:
                user.photo = form.cleaned_data["photo"]
            user.save()

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "exists": True,
                    "message": "Settings updated successfully.",
                    "updated_fields": {
                        "username": user.username,
                        "tournament_nickname":user.tournament_nickname,
                        "description": user.description,
                    }
                })

        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "exists": False,
                    "message": "Validation failed.",
                    "errors": form.errors,
                }, status=400)

    else:
        form = ProfileSettingsForm(initial={
            "username": user.username,
            "description": user.description,
        })

    return render(request, "pong_app/profile_settings.html", {
        "form": form, "username": user.username, 
        "tournament_nickname":user.tournament_nickname,
        "description":user.description,
        })

@login_required(login_url='/login/')
def blocked_people(request):
    main_user = request.user
    if request.method == "GET":
        block_list = main_user.blocked_users.all()
        return render(request, "pong_app/blockedPeople.html", {"block_list": block_list})
    return JsonResponse("Error")

@login_required(login_url='/login/')
def friend_requests(request):
    main_user = request.user

    if request.method == "GET":
        friend_requests = FriendRequest.objects.filter(receiver=main_user)
        return render(request, "pong_app/friend_requests.html", {"friend_requests": friend_requests, "username":main_user.username})

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

@login_required(login_url='/login/')
def find_friend(request):
    if request.method == "POST":
        form = FiendFriendForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            try:
                user = User.objects.get(username=username)
                return JsonResponse({"exists": True, "username": user.username})
            except User.DoesNotExist:
                return JsonResponse({"exists": False, "message": "User not found."})
        else:
            return JsonResponse({"exists": False, "message": "Invalid data."})

    if request.user.is_authenticated:
        return render(request, "pong_app/index.html", {"user_links_template": "pong_app/user_links_authenticated.html"})
    else:
        return render(request, "pong_app/index.html", {"user_links_template": "pong_app/user_links_guest.html"})

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





#Chat
@login_required(login_url='/login/')
def chat(request):
    friend_obj = Friend.objects.get(owner=request.user)

    return render(request, 'pong_app/chat.html', {
        "friends": friend_obj.friends.all(),
        "current_user": request.user.username,
    })

@login_required(login_url='/login/')
def invite_to_game(request):
    return render(request, 'pong_app/invite_to_game.html')





# Pong Game
@login_required(login_url='/login/')
def find_lobby(request):
    if request.method == "POST":
        form = FiendLobbyForm(request.POST)
        
        if form.is_valid():
            lobby_name = form.cleaned_data["lobby_name"]
            return JsonResponse({"exists": True, "lobby_name": lobby_name})
        else:
            return JsonResponse({"exists": False, "message": "Invalid data."})
    return render(request, 'pong_app/find_lobby.html')

@login_required(login_url='/login/')
def pong_lobby(request, room_lobby):
    if len(room_lobby) < 1:
        return render(request, 'pong_app/find_lobby.html',
                      {'error_message': 'Lobby must be at least 1 character long.'})
    elif len(room_lobby) > 8:
        return render(request, 'pong_app/find_lobby.html',
                      {'error_message': 'Lobby cannot be more than 8 characters.'})
    if not all(c.isalnum() for c in room_lobby):
        return render(request, 'pong_app/find_lobby.html',
                      {'error_message': 'Lobby can only contain letters and numbers.'})
    user = request.user
    if(user.lobby and user.lobby != f'game_{room_lobby}'):
        return render(request, 'pong_app/pong_lobby.html', {'room_lobby': user.lobby[5:]})

    return render(request, 'pong_app/pong_lobby.html', {'room_lobby': room_lobby})

@login_required(login_url='/login/')
def bot(request):
    return render(request, 'pong_app/bot.html')
    
def check_tournament(tournament_id):
    contract, web3 = blockchain.contract_creation()
    games = []
    for game_id in range(1, 4):
        try:
            is_approved = contract.functions.getApproval(tournament_id, game_id).call()
            game = contract.functions.getGame(tournament_id, game_id).call()
            if game[1] != 0 and is_approved:
                games.append(game)  # If the game ID is non-zero, it exists
        except Exception as e:
            print(f"Error retrieving game {game_id}: {e}")
    return games


@login_required(login_url='/login/')
def find_tournament(request):
    main_user = request.user
    if request.method == "POST":

        if not (main_user.wallet_address and main_user.wallet_prt_key):
            return JsonResponse({"exists": False, "message": "Wallet data is missing."}, status=403)
        
        form = FiendTournamentForm(request.POST)
        if form.is_valid():
            tournament_name = form.cleaned_data["tournament_name"]
            room = tournament_manager.get_or_create_room(tournament_name, True)
            results = check_tournament(tournament_name)

            if(results and not room):
                if(main_user.tournament_lobby == room):
                    main_user.tournament_lobby = None
                    main_user.save()
                return JsonResponse({"exists": False, "results": results})
            elif main_user.tournament_lobby:
                tournament_name = main_user.tournament_lobby

            return JsonResponse({"exists": True, "tournament_name": tournament_name})
        else:
            return JsonResponse({"exists": False, "message": "Invalid data."})
    
    return render(request, 'pong_app/find_tournament.html')

@login_required(login_url='/login/')
def tournament(request, tournament_id):
    main_user = request.user
    results = check_tournament(tournament_id)
    room = tournament_manager.get_or_create_room(tournament_id, True)
    if(results and not room):
        if(main_user.tournament_lobby == tournament_id):
            main_user.tournament_lobby = None
            main_user.save()
        return render(request, 'pong_app/find_tournament.html')
    if(main_user.tournament_lobby and main_user.tournament_lobby != tournament_id):
        return render(request, 'pong_app/tournament.html', {
        'tournament_id': main_user.tournament_lobby,
        'tournament_nickname': main_user.tournament_nickname,                                           
        })
    else:
        return render(request, 'pong_app/tournament.html', {
            'tournament_id': tournament_id,
            'tournament_nickname': main_user.tournament_nickname,                                           
        })





# Doublejack Game
@login_required(login_url='/login/')
def doublejack(request, room_lobby):
    return render(request, 'pong_app/doublejack.html', {'room_lobby':room_lobby})


@login_required(login_url='/login/')
def find_doublejack(request):
    if request.method == "POST":
        form = FindDoublejackForm(request.POST)
        if form.is_valid():
            doublejack_name = form.cleaned_data["doublejack_name"]
            return JsonResponse({"exists": True, "doublejack_name": doublejack_name})
        else:
            return JsonResponse({"exists": False, "message": "Invalid data."})
    return render(request, 'pong_app/find_doublejack.html')
