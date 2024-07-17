from django import forms
from django_select2.forms import Select2Widget
from .models import Players
from overunder.models import TeamData

class PlayerPredictionForm(forms.Form):
    player_name = forms.ModelChoiceField(
        queryset=Players.objects.all(),
        widget=Select2Widget,
        empty_label=None,
        label='Player Name'
    )
    score_threshold = forms.FloatField(
        label='Score Over How Many Points',
        widget=forms.TextInput(attrs={'class': 'vegas-line-input-box', 'type': 'text', 'id': 'vegas_line', 'name': 'vegas_line'})
    )
    opponent_team = forms.ModelChoiceField(
        queryset=TeamData.objects.all(),
        widget=Select2Widget,
        empty_label="Any Team",
        required=False,
        label='Opponent Team'
    )
