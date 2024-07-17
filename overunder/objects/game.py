import os
from django.conf import settings
from nba_api.stats.endpoints import leaguegamelog
from ..misc.helperfunctions import get_seasons
from .team import Team
import time
import pandas as pd

# The Game class is responsible for getting game logs to create the dataframe for training the model. It is able to get the game logs for n season
# using the get_game_logs function, as well as getting the team metrics for each game using the get_team_metrics_for_games function, which takes
# in the dataframe that get_game_logs creates. Both functions first try to read from the csv file, and if not present, will create them.

csv_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'overunder', 'csvs')

class Game:
    @staticmethod
    def get_game_logs(num_years):
        game_log_path = os.path.join(csv_path, "game_log.csv")
        try:
            game_log = pd.read_csv(game_log_path, index_col=False)
            return game_log
        except:
            years = get_seasons(num_years)
            game_log = []

            for year in years:
                games = leaguegamelog.LeagueGameLog(season=year, season_type_all_star="Regular Season").get_data_frames()[0].reset_index(drop=True)
                time.sleep(0.6)
                games.insert(loc=1, column="SEASON", value=year)
                game_log.append(games)

            game_log = pd.concat(game_log).reset_index(drop=True)
            game_log.to_csv(game_log_path, index=False)
            return game_log
    
    @staticmethod
    def get_team_metrics_for_games(game_log):
        game_metrics_path = os.path.join(csv_path, "game_logs_metrics.csv")
        try:
            game_metrics = pd.read_csv(game_metrics_path, index_col=False)
            return game_metrics
        except:
            game_metrics = []

            for game_id, game in game_log.groupby("GAME_ID"):
                if (len(game)) < 2: continue
                cur_season = game.SEASON.iloc[0]
                
                team_a = Team().set_team(season=cur_season, team_id=game.iloc[0].TEAM_ID)
                team_b = Team().set_team(season=cur_season, team_id=game.iloc[1].TEAM_ID)
                total_points = game.iloc[0].PTS + game.iloc[1].PTS
                
                combined_stats = pd.concat([team_a.stats.add_suffix("_A"), team_b.stats.add_suffix("_H")], axis=1)
                combined_stats["TOTAL_POINTS"] = total_points
                
                game_metrics.append(combined_stats)
                
            game_metrics = pd.concat(game_metrics, axis=0).reset_index(drop=True)
            game_metrics.to_csv(game_metrics_path, index=False)
            return game_metrics
