from django.contrib import admin
from django.urls import path, re_path, register_converter

from . import views
from . import converters


urlpatterns = [
    path('', views.index),
    re_path(r'calculator/', views.calculator, name="index"),
    path('cats/<int:cat_id>/', views.categories),
    path('cats/<slug:cat_slug>/', views.categories_by_slug),
]