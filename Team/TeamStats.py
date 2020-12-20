from .Team import Team
import pandas as pd


class TeamStats:
    def __init__(self, team_list, current_season):
        previous_season_stats = pd.read_csv(f"data/season_rankings/{current_season-1}.csv")["TEAM_ID"].to_numpy().tolist()
        team_map = {}
        for team_id in team_list:
            team_map[team_id] = Team(team_id,1-(previous_season_stats.index(team_id)/30))
        self.team_map = team_map
        previous_season = current_season -1
        file_path = f"./data/head_to_head/{previous_season}.csv"
        self.head_to_head_frame = pd.read_csv(file_path)
        self.count = 0

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

    def get_head_to_head_data(self, home_team_id, away_team_id):
        self.count += 1
        home_team_record  = self.head_to_head_frame.query(f"Team == {str(home_team_id)}")
        head_to_head_string =  home_team_record[str(away_team_id)].iloc[0]
        head_to_head_list =  head_to_head_string.split("-")
        return [int(i) for i in head_to_head_list]