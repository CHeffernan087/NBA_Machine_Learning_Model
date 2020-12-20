import pandas as pd
NUMBER_OF_GAMES =3


class Team:
    def __init__(self, team_id, team_rating):
        self.team_id = team_id
        self.game_history = [0]*NUMBER_OF_GAMES
        self.num_home_wins = 0
        self.num_home_loses = 0
        self.num_away_wins = 0
        self.num_away_loses = 0
        self.number_games_played = 0
        self.points_per_game = 0
        self.points_conceded_per_game = 0
        self.team_rating = team_rating

    @staticmethod
    def get_franchise(team_name):
        name_array = team_name.split(" ")
        if name_array[0] == "Los":
            franchise = f"LA {name_array[2]}"
        elif len(name_array) > 2 and name_array[0] != "Portland":
            franchise = f"{name_array[0]} {name_array[1]}"
        else:
            franchise = name_array[0]
        return franchise

    def getCurrentForm(self):
        wins = 0
        loses = 0

        for game in self.game_history:
            if game == 1:
                wins += 1
            else:
                loses += 1
        return self.game_history

    def parseGame(self, game):
        home_team = game["HOME_TEAM"]
        home_team_win = game["RESULT"]

        team_has_won = False
        is_home_team = self.team_id == home_team

        if(is_home_team):
            self.points_per_game += game["HOME_TEAM_POINTS"]
            self.points_conceded_per_game += game["AWAY_TEAM_POINTS"]
            if(home_team_win):
                team_has_won = True
                self.num_home_wins += 1
            else:
                self.num_home_loses += 1
        else:
            self.points_per_game += game["AWAY_TEAM_POINTS"]
            self.points_conceded_per_game += game["HOME_TEAM_POINTS"]
            if(not home_team_win):
                team_has_won = True
                self.num_away_wins += 1
            else:
                self.num_away_loses += 1


        result = 1 if team_has_won else 0
        self.number_games_played +=1
        self.game_history.insert(0, result)
        if len(self.game_history) > NUMBER_OF_GAMES:
            self.game_history.pop()

    def getRating(self):
        return self.team_rating

    def getWins(self):
        return self.num_away_wins + self.num_home_wins

    def getLoses(self):
        return self.num_away_loses + self.num_home_loses

    def getNumberGamesPlayed(self):
        return self.getWins() + self.getLoses()

    def getPointsPerGame(self):
        number_games_played = self.getNumberGamesPlayed()
        if number_games_played == 0:
            return 0
        else:
            return int(self.points_per_game / self.getNumberGamesPlayed())

    def getPointsConcededPerGame(self):
        number_games_played = self.getNumberGamesPlayed()
        return 0 if number_games_played ==0  else int(self.points_conceded_per_game /self.getNumberGamesPlayed())

    def getTeamRecord(self):
        return {
            "HOME_WINS": round((1+self.num_home_wins) / (1+self.num_home_wins + 1+self.num_home_loses),3),
            "HOME_LOSES": round((1+self.num_home_loses) / (1+self.num_home_wins + 1+self.num_home_loses),3),
            "AWAY_WINS": round((1+self.num_away_wins) / (1+self.num_away_wins+1+self.num_away_loses),3),
            "AWAY_LOSES": round((1+self.num_away_loses) / (1+self.num_away_wins + 1+self.num_away_loses),3),
        }

