import os
from django.conf import settings
from nba_api.stats.static.teams import find_team_by_abbreviation, find_team_name_by_id, find_teams_by_full_name, get_teams
from nba_api.stats.endpoints import teamestimatedmetrics
from ..misc.helperfunctions import get_seasons
import time
import pandas as pd

# The team object holds a team's name, id, the dataframe for its info, and the dataframe for its stats. A team can be created through
# set_team which needs a season to pull the team's stats from, as well as either the name of the team or the team's id. It will only
# read from a csv file which should be created upon creating an instance of DataHandler.

csv_path = os.path.join(os.path.dirname(settings.BASE_DIR), 'overunder', 'csvs')

class Team:
    def __init__(self, name=None, team_id=None):
        self.name = name
        self.team_id = team_id
        self.info = None
        self.stats = None
        
    @staticmethod
    def set_team(season, name=None, team_id=None):
        team_stats_path = os.path.join(csv_path, "team_stats.csv")
        try:
            all_teams = pd.read_csv(team_stats_path, index_col=False)
        except:
            print("INITIALIZE TEAM STATS CSV")

        if (name):
            if (len(name) == 3):
                name = name.lower()
                team_df = all_teams.loc[all_teams["abbreviation"] == name]
            else:
                team_df = all_teams.loc[all_teams["nickname"] == name]
        else:
            team_df = all_teams.loc[all_teams["id"] == team_id]
            
        if (team_df.empty):
            return False

        team_df = team_df.loc[team_df["SEASON"] == season]
        
        info = pd.DataFrame([team_df.iloc[0, 0:6]]).reset_index(drop=True)
        stats = pd.DataFrame([team_df.iloc[0, 7:-1]]).reset_index(drop=True)
        name = info.full_name[0]
        team_id = info.id[0]

        team = Team(name=name, team_id=team_id)
        team.info, team.stats = info, stats

        return team
    
    @staticmethod
    def team_stats_to_csv(num_years):
        team_stats_path = os.path.join(csv_path, "team_stats.csv")
        try:
            all_teams = pd.read_csv(team_stats_path, index_col=False)
            teams = get_teams()
            team_stats = []
            for team in teams:
                cur_team = Team()._get_team(1, team_id=team["id"])
                cur_season = get_seasons()[0]
                all_teams = all_teams[all_teams["TEAM_ID"] == cur_team.team_id and all_teams["SEASON"] == cur_season]
        except:
            teams = get_teams()
            team_stats = []

            for team in teams:
                cur_team = Team()._get_team(num_years, team_id=team["id"])
                for i in range(len(cur_team.stats)):
                    team_stats.append(pd.concat([cur_team.info.reset_index(drop=True), cur_team.stats.loc[[i]].reset_index(drop=True)], axis=1))

            team_stats = pd.concat(team_stats).reset_index(drop=True).map(lambda s: s.lower() if type(s) == str else s)

        
        team_stats.to_csv(team_stats_path, index=False)
            
    @staticmethod
    def _get_team(num_years, name=None, team_id=None):
        team = Team(name=name, team_id=team_id)

        team.info = team._get_team_info()
        time.sleep(0.5)
        team.stats = team._get_team_stats_by_info(num_years)
        time.sleep(0.5)

        team.team_id = team.info.id[0]
        team.name = team.info.full_name[0]

        return team

    def _get_team_info(self):
        if (self.name):
            if (len(self.name) == 3):
                info = pd.Dataframe([find_team_by_abbreviation(self.name)])
            else:
                info = pd.DataFrame.from_dict(find_teams_by_full_name(self.name))
        else:
            info = pd.DataFrame([find_team_name_by_id(self.team_id)])
        return info

    def _get_team_stats_by_info(self, num_years):
        years = get_seasons(num_years)

        team_id = self.info["id"][0]
        stats_log = []

        for year in years:
            stats = teamestimatedmetrics.TeamEstimatedMetrics(season=year).get_data_frames()[0]
            time.sleep(0.6)
            stats.insert(loc=7, column="SEASON", value=year)
            stats = stats[stats["TEAM_ID"] == team_id].reset_index(drop=True)
            stats_log.append(stats)

        stats_log = pd.concat(stats_log).reset_index(drop=True)

        return stats_log
