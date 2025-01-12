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

def	wallet(request):
	return render(request, 'pong_app/wallet.html')

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

def	wallet(request):
	return render(request, 'pong_app/wallet.html')



def bot(request):
    return render(request, 'pong_app/bot.html')

@login_required(login_url='/login/')
def chat(request):
    groups = ChatGroup.objects.filter(members=request.user)
    friend_obj = Friend.objects.get(owner=request.user)
    # friends = friend_obj.friends.all()

    # online_users = friends.filter(last_activity__gte=now() - timedelta(minutes=1))
    # friends_with_status = [
    #     {
    #         'username': friend.username,
    #         'photo': friend.photo.url if friend.photo else '/static/default_user_photo.jpg',
    #         'is_online': friend in online_users
    #     }
    #     for friend in friends
    # ]
    # print(friends_with_status)
    return render(request, 'pong_app/chat.html', {
        "friends": friend_obj.friends.all(),
        "current_user": request.user.username,
        "groups": groups,
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
    username = user.username
    admin_user = get_object_or_404(User, username=username)
    group, created = ChatGroup.objects.get_or_create(name=room_lobby)
    group.save()


    if created:
        group.owner = admin_user
        group.save()

    group.members.add(user)
    group.save()

    return render(request, 'pong_app/pong_lobby.html', {'room_lobby': room_lobby})



import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.http import JsonResponse

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


from django.shortcuts import render
from django.http import HttpResponse
from web3 import Web3

# Function to get Web3 instance
def get_web3_instance():
    return Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))  # Adjust provider URL as needed

# Function to load the smart contract
def load_contract(abi_path, contract_address):
    with open(abi_path, 'r') as abi_file:
        abi_json = json.load(abi_file)
    contract_abi = abi_json["abi"]
    #print(abi_json["address"])
    web3 = get_web3_instance()
    return web3.eth.contract(address=contract_address, abi=contract_abi)

def bind_wallet(request):
    if request.method == 'POST':
        wallet_address = request.POST.get('address')
        private_key = request.POST.get('private_key')
        user = request.user
        score = Score.objects.get(user=user)
        print(user.username)
        print(score.score)
		

        # Save wallet data (this could also be stored in the database)
        wallet_data = {
            'address': wallet_address,
            'private_key': private_key,
        }
        print(wallet_address, private_key)

        # Add user to the blockchain
        try:
            web3 = get_web3_instance()
            if web3.is_connected():
                print("web3 is connected")
            contract_address = "0x3522DB9120183097fE82842792C7516B9093dcbE"  # Replace with your contract address
            abi_path = "/Users/tanya/blockchain-for-42/transcendence/ft_transcendence/transcendence/blockchain/build/contracts/WinnerStorage.json"  # Replace with the correct path to your ABI JSON file

            contract = load_contract(abi_path, contract_address)

            # Build the transaction
            transaction = contract.functions.addUser(user.username, score.score, True).build_transaction({
                'from': wallet_address,
                'gas': 2000000,
                'gasPrice': web3.eth.gas_price,
                'nonce': web3.eth.get_transaction_count(wallet_address),
            })

            # Sign and send the transaction
            signed_tx = web3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Return the transaction hash as confirmation
            return HttpResponse(f"User added to blockchain. Transaction Hash: {web3.to_hex(tx_hash)}")
        except Exception as e:
            return HttpResponse(f"Error adding user to blockchain: {str(e)}")

    return render(request, 'pong_app/wallet.html')

