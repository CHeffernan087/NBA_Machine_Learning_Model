from .Team import Team

HOME_TEAM = 0
AWAY_TEAM = 1
RESULT = 2


class TeamStats:

    def __init__(self, team_list):
        team_map = {}
        for team_id in team_list:
            team_map[team_id] = Team(team_id)
        self.team_map = team_map

    def recordGame(self, game):
        home_team = self.team_map[game[HOME_TEAM]]
        home_team.parseGame(game)

        away_team = self.team_map[game[AWAY_TEAM]]
        away_team.parseGame(game)

    def getTeamRecord(self, team_id):
        current_team = self.team_map[team_id]
        return current_team.getCurrentForm()

    def getTeam(self, team_id):
        return self.team_map[team_id]
