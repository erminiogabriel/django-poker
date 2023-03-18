from django.urls import path

from . import views

app_name = 'poker'
urlpatterns = [
    path('', views.IndexView, name='index'),
    path('<int:pk>/', views.GameView, name='game'),
    path('gamedata/', views.GameData, name='gamedata'),
    path('registerplayer/', views.RegisterPlayer, name='registerplayer'),
    path('startgame/', views.StartGame, name='startgame'),
    path('fold/', views.Fold, name='fold'),
    path('check/', views.Check, name='check'),
    path('bet/', views.Bet, name='bet'),
]