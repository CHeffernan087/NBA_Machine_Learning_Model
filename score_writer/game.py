from collections import OrderedDict

NUMBER_OF_GAMES = 3


class Game(OrderedDict):
    """
    Represents a game played. This class is used to write the relevant feature data to the csv.
    Instances of this game are an ordered dictionary (a regular python dictionary that keeps track of the orders
    key value pairs were added. Needed for adding features to the csv. Also why HOME_TEAM_WINS must be last, as it is
    the output/label value. __setitem__ adds key value pairs to the dict. These keys denote features.
    """

    # TODO remove unused params
    def __init__(self, home_team, away_team, home_team_win, home_team_elo, away_team_elo,
                 home_team_raptor, away_team_raptor, home_team_hth, away_team_hth):
        """
        Adds the features (keys) to the OrderedDict along with their values

        :param home_team: instance of Team representing home team
        :param away_team:instance of Team representing away team
        :param home_team_win: boolean flag 0/1 denoting if the home team has won
        :param home_team_elo:
        :param away_team_elo:
        :param home_team_raptor:
        :param away_team_raptor:
        :param home_team_hth:
        :param away_team_hth:
        """
        super().__init__()

        home_team_record = home_team.getTeamRecord()
        away_team_record = away_team.getTeamRecord()
        super().__setitem__("HOME_TEAM_HOME_WINS", home_team_record["HOME_WINS"])
        # super().__setitem__("HOME_TEAM_HOME_LOSES", home_team_record["HOME_LOSES"])
        super().__setitem__("HOME_TEAM_ROAD_WINS", home_team_record["AWAY_WINS"])
        super().__setitem__("HOME_TEAM_ROAD_LOSES", home_team_record["AWAY_LOSES"])

        # super().__setitem__("AWAY_TEAM_HOME_WINS", away_team_record["HOME_WINS"])
        # super().__setitem__("AWAY_TEAM_HOME_LOSES", away_team_record["HOME_LOSES"])
        super().__setitem__("AWAY_TEAM_ROAD_WINS", away_team_record["AWAY_WINS"])
        super().__setitem__("AWAY_TEAM_ROAD_LOSES", away_team_record["AWAY_LOSES"])

        super().__setitem__("HOME_TEAM_HTH_RECORD", home_team_hth)
        # super().__setitem__("AWAY_TEAM_HTH_RECORD", away_team_hth)

        '''
        get the teams record of the last 3 games
        '''
        home_team_history = home_team.getCurrentForm()
        away_team_history = away_team.getCurrentForm()

        for game in range(0,NUMBER_OF_GAMES):
            if game < 2:
                super().__setitem__(f"AWAY_TEAM_FORM_{game}", away_team_history[game])
            else:
                super().__setitem__(f"HOME_TEAM_FORM_{game}", home_team_history[game])


        super().__setitem__("HOME_TEAM_WIN_RECORD", home_team.getWins())
        super().__setitem__("AWAY_TEAM_WIN_RECORD", away_team.getWins())

        super().__setitem__("HOME_TEAM_PPG", home_team.getPointsPerGame())
        super().__setitem__("HOME_TEAM_PAPG", home_team.getPointsConcededPerGame())
        super().__setitem__("AWAY_TEAM_PPG", away_team.getPointsPerGame())
        super().__setitem__("AWAY_TEAM_PAPG", away_team.getPointsConcededPerGame())

        '''
        add the elo ratings for each game from https://projects.fivethirtyeight.com/nba-model/nba_elo.csv
        '''
        # super().__setitem__("HOME_TEAM_ELO", home_team_elo)
        # super().__setitem__("AWAY_TEAM_ELO", away_team_elo)

        '''
        MAKE SURE THIS IS ADDED LAST
        '''
        super().__setitem__("HOME_TEAM_WINS", home_team_win)

    # TODO unused function - can delete
    @staticmethod
    def hasSufficientData(home_team):
        """
        checks that the home team has played at least ten games

        :param home_team: instance of team representing home
        :return: true if played more than 10 else 0
        """
        number_of_games = home_team.getNumberGamesPlayed()

        if number_of_games > 10:
            sufficient_data = True
        else:
            sufficient_data = False

        return sufficient_data

    # TODO unused function - can delete
    def _get_rankings(self, team_id, game_date):
        team_rankings = self._rankings.query(f'TEAM_ID == "{team_id}"').sort_values(by=['STANDINGSDATE'])
        team_rank_on_date = team_rankings.query(f'STANDINGSDATE == "{game_date}"')

        team_home_record = team_rank_on_date['HOME_RECORD'].iloc[0].split("-")
        team_home_wins, team_home_loses = map(int, team_home_record)

        team_road_record = team_rank_on_date['ROAD_RECORD'].iloc[0].split("-")
        team_road_wins, team_road_loses = map(int, team_road_record)
        return team_home_wins, team_home_loses, team_road_wins, team_road_loses
