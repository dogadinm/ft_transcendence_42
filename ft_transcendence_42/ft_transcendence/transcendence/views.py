from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.http import JsonResponse


# Create your views here.

def index(request):
    # posts = Post.objects.all().order_by('id').reverse()

    # Pagination
    # p = Paginator(posts, 10)
    # numb_page = request.GET.get("page")
    # post_page = p.get_page(numb_page)


    return render(request, "pong_app/index.html")


def login(request):
    return render(request, 'pong_app/login.html')
def register(request):
    return render(request, 'pong_app/register.html')

def pong(request):
    return render(request, 'pong_app/pong.html')

def categories(request, cat_id):
    return HttpResponse(f"<h1>Categories<h1><p>id: {cat_id}<p>")

def archive(request, year):
    if year > 2023:
        return redirect('/')
    return HttpResponse(f"<h1>Archive<h1><p>Year: {year}<p>")

def categories_by_slug(request, cat_slug):
    if request.POST:
        print(request.POST)
    return HttpResponse(f"<h1>Categories<h1><p>Slug: {cat_slug}<p>")

def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Not found page<h1>")


def calculator(request):
    return render(request, 'pong_app/calculator.html', {})

def cha_view(request):
    return render(request, 'pong_app/chat.html')
