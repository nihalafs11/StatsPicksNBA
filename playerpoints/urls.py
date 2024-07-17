from django.urls import path
from . import views

app_name = 'playerpoints'

urlpatterns = [
    path('', views.player_predictions, name='player_predictions'),
    path('api/get_player_image_url/', views.get_player_image_url, name='get_player_image_url'),
]
