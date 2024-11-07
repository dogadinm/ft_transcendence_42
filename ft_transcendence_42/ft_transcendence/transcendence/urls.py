from django.contrib import admin
from django.urls import path, re_path

from . import views
from . import converters


urlpatterns = [
    path('', views.index, name='index'),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    re_path(r'pong/', views.pong, name="pong"),
    re_path(r'calculator/', views.calculator, name="calculator"),
]