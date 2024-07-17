from django import forms
from django_select2.forms import Select2Widget
from .models import TeamData

class PredictionForm(forms.Form):
    team_away_name = forms.ModelChoiceField(
        queryset=TeamData.objects.all(),
        label="Away Team",
        widget=Select2Widget,
        to_field_name="team_input",  # This specifies that `team_input` is used as the value when form is submitted
        empty_label="Select Away Team"
    )
    team_home_name = forms.ModelChoiceField(
        queryset=TeamData.objects.all(),
        label="Home Team",
        widget=Select2Widget,
        to_field_name="team_input",  # Similarly for the home team
        empty_label="Select Home Team"
    )
    vegas_line = forms.FloatField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['team_away_name'].label_from_instance = lambda obj: f"{obj.team_name}"
        self.fields['team_home_name'].label_from_instance = lambda obj: f"{obj.team_name}"
