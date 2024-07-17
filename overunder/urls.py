from django.urls import path
from . import views

app_name = 'overunder'

urlpatterns = [
    path('', views.index, name='index'),
    path('get-team-logo/', views.get_team_logo, name='get_team_logo')
    # other paths
]
