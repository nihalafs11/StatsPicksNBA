import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from .forms import PlayerPredictionForm
from overunder.models import TeamData
from .models import Players
import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.metrics import make_scorer, f1_score, precision_score, recall_score


seasons_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'playerpoints', 'seasons')

seasons_dict = {
    '2020-21': os.path.join(seasons_path, 'nba-player-stats-2020-2021-Regular-Season.csv'),
    '2021-22': os.path.join(seasons_path, 'nba-player-stats-2021-2022-Regular-Season.csv'),
    '2022-23': os.path.join(seasons_path, 'nba-player-stats-2022-2023-Regular-Season.csv'),
    '2023-24': os.path.join(seasons_path, 'nba-player-stats-2023-2024-Regular-Season.csv'),
}


def generate_player_gamelog_csv(player_name):
    player_dict = players.get_players()
    player = [p for p in player_dict if p['full_name'].lower() == player_name.lower()]
    if not player:
        print(f"Player '{player_name}' not found.")
        return None, "Player not found."
    player_id = player[0]['id']

    all_seasons_gamelog_df = pd.DataFrame()
    for season, file_path in seasons_dict.items():
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=season)
        gamelog_df = gamelog.get_data_frames()[0]
        gamelog_df['Season'] = season  
        all_seasons_gamelog_df = pd.concat([all_seasons_gamelog_df, gamelog_df.dropna()], ignore_index=True)

    csv_file_name = f"{player_name.lower().replace(' ', '_')}_gamelog_2020_to_2024.csv"
    all_seasons_gamelog_df.to_csv(csv_file_name, index=False)
    return csv_file_name, None

def prepare_player_gamelog(csv_filename, opponent_team=''):
    player_gamelog = pd.read_csv(csv_filename)
    player_gamelog['GAME_DATE'] = pd.to_datetime(player_gamelog['GAME_DATE'], format='%b %d, %Y')
    player_gamelog.sort_values('GAME_DATE', ascending=True, inplace=True)

    player_gamelog['Rolling_PTS_5'] = player_gamelog['PTS'].shift().rolling(window=5).mean()
    player_gamelog['Home_Game'] = player_gamelog['MATCHUP'].apply(lambda x: 0 if '@' in x else 1)
    player_gamelog['Avg_PTS_against_Opponent'] = player_gamelog[player_gamelog['MATCHUP'].str.contains(opponent_team)]['PTS'].mean() if opponent_team else player_gamelog['PTS'].mean()

    return player_gamelog

def merge_with_season_summary(player_gamelog, player_name):
    combined_season_summary = pd.DataFrame()
    for season, file_path in seasons_dict.items():
        season_df = pd.read_csv(file_path)
        season_df['Season'] = season  
        combined_season_summary = pd.concat([combined_season_summary, season_df], ignore_index=True)

    player_season_summary = combined_season_summary[combined_season_summary['NAME'].str.lower() == player_name.lower()]
    merged_data = pd.merge(player_gamelog, player_season_summary[['ORtg', 'DRtg', 'Season']], on='Season', how='left')
    return merged_data

def run_model(player_name, score_threshold, opponent_team=''):
    csv_filename, error = generate_player_gamelog_csv(player_name)
    if error:
        return None, error
    
    try:
        player_gamelog = prepare_player_gamelog(csv_filename, opponent_team)
        player_gamelog = merge_with_season_summary(player_gamelog, player_name)

        player_gamelog['Scored_Over_X'] = (player_gamelog['PTS'] > score_threshold).astype(int)

        minimum_games_required = 10  
        if len(player_gamelog) < minimum_games_required or player_gamelog['Scored_Over_X'].nunique() < 2:
            return None, f"Insufficient data to provide predictions. Need at least {minimum_games_required} games and at least two classes in target."

        features = player_gamelog[['MIN', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'Rolling_PTS_5', 'Avg_PTS_against_Opponent', 'Home_Game', 'ORtg', 'DRtg']]
        target = player_gamelog['Scored_Over_X']

        pipeline = make_pipeline(SimpleImputer(strategy='mean'), LogisticRegression(max_iter=100000))
        accuracy_scores = cross_val_score(pipeline, features, target, cv=10, scoring='accuracy')
        precision_scores = cross_val_score(pipeline, features, target, cv=10, scoring=make_scorer(precision_score, zero_division=1))
        recall_scores = cross_val_score(pipeline, features, target, cv=10, scoring='recall')
        f1_scores = cross_val_score(pipeline, features, target, cv=10, scoring=make_scorer(f1_score, zero_division=1))

        results = {
            'accuracy': accuracy_scores.mean(),
            'precision': precision_scores.mean(),
            'recall': recall_scores.mean(),
            'f1_score': f1_scores.mean()
        }
    finally:
        if os.path.exists(csv_filename):
            os.remove(csv_filename)
    
    return results, None 


def player_predictions(request):
    players = Players.objects.all()
    teams = TeamData.objects.all()

    if request.method == 'POST':
        form = PlayerPredictionForm(request.POST)
        if form.is_valid():
            player_name = form.cleaned_data['player_name'].name
            score_threshold = form.cleaned_data['score_threshold']
            opponent_team = form.cleaned_data.get('opponent_team')
            opponent_team_abbr = opponent_team.abbreviation if opponent_team else ""

            results, error = run_model(player_name, score_threshold, opponent_team_abbr)
            if error:
                return JsonResponse({'error': error})
            return JsonResponse(results)
        else:
            print(form.errors)  
            return JsonResponse({'error': 'Form is not valid, errors: ' + str(form.errors)})

    else:
        form = PlayerPredictionForm()
    return render(request, 'player_points.html', {
        'form': form, 
        'players': players, 
        'teams': teams
    })

def get_player_image_url(request):
    player_id = request.GET.get('player_id')
    if player_id:
        try:
            player = Players.objects.get(id=player_id)
            return JsonResponse({'picture_url': player.picture}, safe=False)
        except Players.DoesNotExist:
            return JsonResponse({'error': 'Player not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)
