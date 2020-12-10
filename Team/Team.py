

HOME_TEAM = 0
AWAY_TEAM = 1
RESULT = 2

NUMBER_OF_GAMES = 3

class Team():


    def __init__(self, team_id, games):
        self.team_id = team_id
        self.last_five_games = []
        self.games = games

    def getCurrentForm(self):
        wins = 0
        loses = 0

        for game in self.last_five_games:
            if(game ==1):
                wins = wins + 1
            else:
                loses = loses + 1
        return [wins,loses]

    def parseGame(self,game):
        homeTeam = game[HOME_TEAM]
        homeTeamWin = game[RESULT]

        teamHasWon = False
        isHomeTeam = self.team_id == homeTeam

        if(isHomeTeam and homeTeamWin ):
            teamHasWon = True
        elif (not isHomeTeam and not homeTeamWin):
            teamHasWon = True

        result = 1 if teamHasWon else 0

        self.last_five_games.insert(0, result)
        if(len(self.last_five_games) > NUMBER_OF_GAMES):
            self.last_five_games.pop()

    '''
    If you want the record for the 2018-2019 season, just pass in 2019
    '''
    def getTeamRecordForSeaoson(self, season):
        self.games.loc[f'{season}-01-01':f'{season}-07-07']
        test = "blood"

