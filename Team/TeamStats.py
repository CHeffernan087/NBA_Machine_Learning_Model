from .Team import Team


class TeamStats:
    def __init__(self, team_list):
        team_map = {}
        for team_id in team_list:
            team_map[team_id] = Team(team_id)
        self.team_map = team_map

    def recordGame(self, home_away_result_dict):
        home_team = self.team_map[home_away_result_dict["HOME_TEAM"]]
        home_team.parseGame(home_away_result_dict)

        away_team = self.team_map[home_away_result_dict["AWAY_TEAM"]]
        away_team.parseGame(home_away_result_dict)

    def getTeamRecord(self, team_id):
        current_team = self.team_map[team_id]
        return current_team.getCurrentForm()

    def getTeam(self, team_id):
        return self.team_map[team_id]
