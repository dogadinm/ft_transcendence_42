from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    return HttpResponse("Transcendence page")

def categories(request):
    return HttpResponse("<h1>Categories<h1>")