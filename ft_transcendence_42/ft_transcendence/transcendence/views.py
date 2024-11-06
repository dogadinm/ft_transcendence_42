from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect


# Create your views here.

def index(request):
    return render(request, 'pong_app/index.html')

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
