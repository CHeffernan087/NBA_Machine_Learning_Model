from .Team import Team

HOME_TEAM = 0
AWAY_TEAM = 1
RESULT = 2

class TeamStats():

    def __init__(self, teamList):
        team_map = {}
        for team_id in teamList:
            team_map[team_id] = Team(team_id)
        self.team_map = team_map

    def recordGame(self, game):
        homeTeam = self.team_map[game[HOME_TEAM]]
        homeTeam.parseGame(game)

        awayTeam = self.team_map[game[AWAY_TEAM]]
        awayTeam.parseGame(game)

    def getTeamRecord(self, team_id):
        current_team = self.team_map[team_id]
        return  current_team.getCurrentForm()

    def getTeam(self,team_id):
        return self.team_map[team_id]