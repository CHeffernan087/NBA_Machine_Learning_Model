from collections import OrderedDict


class Game(OrderedDict):
    """
    teams are a team object
    """

    def __init__(self, home_team, away_team,home_team_win, home_team_elo, away_team_elo,
                 home_team_raptor, away_team_raptor):
        super().__init__()


        home_team_record = home_team.getTeamRecord()
        away_team_record = away_team.getTeamRecord()
        super().__setitem__("HOME_TEAM_HOME_WINS", home_team_record["HOME_WINS"])
        super().__setitem__("HOME_TEAM_HOME_LOSES", home_team_record["HOME_LOSES"])
        super().__setitem__("HOME_TEAM_ROAD_WINS", home_team_record["AWAY_WINS"])
        super().__setitem__("HOME_TEAM_ROAD_LOSES", home_team_record["AWAY_LOSES"])


        super().__setitem__("AWAY_TEAM_HOME_WINS", away_team_record["HOME_WINS"])
        super().__setitem__("AWAY_TEAM_HOME_LOSES", away_team_record["HOME_LOSES"])
        super().__setitem__("AWAY_TEAM_ROAD_WINS", away_team_record["AWAY_WINS"])
        super().__setitem__("AWAY_TEAM_ROAD_LOSES", away_team_record["AWAY_LOSES"])

        '''
        get the teams record of the last 3 games
        '''
        super().__setitem__("HOME_TEAM_FORM", home_team.getCurrentForm()[0])
        super().__setitem__("AWAY_TEAM_FORM", away_team.getCurrentForm()[0])

        '''
        add the elo ratings for each game from https://projects.fivethirtyeight.com/nba-model/nba_elo.csv
        '''
        # super().__setitem__("HOME_TEAM_ELO", home_team_elo)
        # super().__setitem__("AWAY_TEAM_ELO", away_team_elo)

        super().__setitem__("HOME_TEAM_RAPTOR", home_team_raptor)
        super().__setitem__("AWAY_TEAM_RAPTOR", away_team_raptor)

        '''
        MAKE SURE THIS IS ADDED LAST
        '''
        super().__setitem__("HOME_TEAM_WINS", home_team_win)


    def hasSufficientData(self):
        team_home_wins = super().__getitem__("HOME_TEAM_HOME_WINS")
        team_home_loses = super().__getitem__("HOME_TEAM_HOME_LOSES")

        team_road_wins = super().__getitem__("HOME_TEAM_ROAD_WINS")
        team_road_loses = super().__getitem__("HOME_TEAM_ROAD_LOSES")

        home_games = team_home_wins + team_home_loses
        away_games = team_road_wins + team_road_loses
        number_of_games = home_games + away_games

        if number_of_games > 10:
            sufficient_data = True
        else:
            sufficient_data = False

        return sufficient_data
