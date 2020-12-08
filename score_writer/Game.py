import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from operator import itemgetter
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error
from sklearn import linear_model
from sklearn.model_selection import KFold
import matplotlib.patches as mpatches
from datetime import timedelta, datetime

# header = ["TEAM_ID", "LEAGUE_ID", "SEASON_ID", "STANDINGSDATE", "CONFERENCE", "TEAM", "G", "W", "L", "W_PCT",
#           "HOME_RECORD", "ROAD_RECORD"]
# header = ["LEAGUE_ID", "TEAM_ID", "MIN_YEAR", "MAX_YEAR", "ABBREVIATION", "NICKNAME", "YEARFOUNDED", "CITY", "ARENA",
#           "ARENACAPACITY", "OWNER", "GENERALMANAGER", "HEADCOACH", "DLEAGUEAFFILIATION"]
rankings = pd.read_csv("../data/ranking.csv")
games = pd.read_csv("../data/games.csv")



class Game():

    def getRankings(self,team, game_date):
        team_rankings = rankings.query(f'TEAM_ID == "{team}"').sort_values(by=['STANDINGSDATE'])
        team_rank_on_date = team_rankings.query(f'STANDINGSDATE == "{game_date}"')

        hr = team_rank_on_date['HOME_RECORD'].iloc[0]

        team_home_record = team_rank_on_date['HOME_RECORD'].iloc[0].split("-")
        team_road_record = team_rank_on_date['ROAD_RECORD'].iloc[0].split("-")

        team_home_wins = team_home_record[0]
        team_home_loses = team_home_record[1]

        team_road_wins = team_road_record[0]
        team_road_loses = team_road_record[1]
        return [team_home_wins, team_home_loses, team_road_wins, team_road_loses]


    '''
    get the records
    '''
    def __init__(self, homeTeam, awayTeam, game_date):


        team_home_wins, team_home_loses, team_road_wins, team_road_loses = self.getRankings(homeTeam, game_date)
        self.home_team_home_wins = team_home_wins
        self.home_team_home_loses = team_home_loses
        self.home_team_road_wins = team_road_wins
        self.home_team_road_loses = team_road_loses

        team_home_wins, team_home_loses, team_road_wins, team_road_loses = self.getRankings(awayTeam, game_date)
        self.away_team_home_wins = team_home_wins
        self.away_team_home_loses = team_home_loses
        self.away_team_road_wins = team_road_wins
        self.away_team_road_loses = team_road_loses



'''
for every game: 
    make a game object:
        home team | away team | homeTeamHomeRec | awayTeamHomeRec | hometeamAwayRec | awayTeamAwayRec
'''


'''
iterate over games - make game obj
'''

print(games['GAME_DATE_EST'][0])
gameList = []


for index, game_date in enumerate(games['GAME_DATE_EST']):
    # year, month, day = game_date.split("-")
    # current_date = datetime(int(year), int(month), int(day))
    home_team = games['HOME_TEAM_ID'][index];
    away_team = games['VISITOR_TEAM_ID'][index];
    gameList.append(Game(home_team, away_team, game_date))
    break;

