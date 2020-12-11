NUMBER_OF_GAMES = 3


class Team:
    def __init__(self, team_id):
        self.team_id = team_id
        self.game_history = []

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
        return [wins, loses]

    def parseGame(self, game):
        home_team = game["HOME_TEAM"]
        home_team_win = game["RESULT"]

        team_has_won = False
        is_home_team = self.team_id == home_team

        if is_home_team and home_team_win:
            team_has_won = True
        elif not is_home_team and not home_team_win:
            team_has_won = True

        result = 1 if team_has_won else 0

        self.game_history.insert(0, result)
        if len(self.game_history) > NUMBER_OF_GAMES:
            self.game_history.pop()
