HOME_TEAM = 0
AWAY_TEAM = 1
RESULT = 2

NUMBER_OF_GAMES = 3


class Team:
    def __init__(self, team_id, games):
        self.team_id = team_id
        self.last_five_games = []
        self.games = games

    def getCurrentForm(self):
        wins = 0
        loses = 0

        for game in self.last_five_games:
            if game == 1:
                wins = wins + 1
            else:
                loses = loses + 1
        return [wins, loses]

    def parseGame(self, game):
        home_team = game[HOME_TEAM]
        home_team_win = game[RESULT]

        team_has_won = False
        is_home_team = self.team_id == home_team

        if is_home_team and home_team_win:
            team_has_won = True
        elif not is_home_team and not home_team_win:
            team_has_won = True

        result = 1 if team_has_won else 0

        self.last_five_games.insert(0, result)
        if len(self.last_five_games) > NUMBER_OF_GAMES:
            self.last_five_games.pop()

    '''
    If you want the record for the 2018-2019 season, just pass in 2019
    '''
    def getTeamRecordForSeason(self, season):
        self.games.loc[f'{season}-01-01':f'{season}-07-07']
        test = "blood"
