from django.urls import path
from . import views


urlpatterns = [
    path('', views.ProfileFormView.as_view(), name="profile"),
    path('game/', views.parse_command, name="game")
]
