from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('game/', views.parse_command, name="game")
]
