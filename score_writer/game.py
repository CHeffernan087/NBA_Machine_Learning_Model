from collections import OrderedDict


class Game(OrderedDict):
    """
    teams are a team object
    """

    def __init__(self, home_team, away_team,home_team_win, home_team_elo, away_team_elo,
                 home_team_raptor, away_team_raptor,home_team_hth, away_team_hth):
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

        super().__setitem__("HOME_TEAM_HTH_RECORD", home_team_hth)
        super().__setitem__("AWAY_TEAM_HTH_RECORD", away_team_hth)

        '''
        get the teams record of the last 3 games
        '''
        home_team_history = home_team.getCurrentForm()
        away_team_history = away_team.getCurrentForm()

        for index, game in enumerate(home_team_history):
            super().__setitem__(f"HOME_TEAM_FORM_{index}", game)
            super().__setitem__(f"AWAY_TEAM_FORM_{index}", away_team_history[index])

        super().__setitem__("HOME_TEAM_WIN_RECORD", home_team.getWins())
        super().__setitem__("AWAY_TEAM_WIN_RECORD", away_team.getWins())

        super().__setitem__("HOME_TEAM_PPG", home_team.getPointsPerGame())
        super().__setitem__("HOME_TEAM_PAPG", home_team.getPointsConcededPerGame())
        super().__setitem__("AWAY_TEAM_PPG", away_team.getPointsPerGame())
        super().__setitem__("AWAY_TEAM_PAPG", away_team.getPointsConcededPerGame())

        '''
        add the elo ratings for each game from https://projects.fivethirtyeight.com/nba-model/nba_elo.csv
        '''
        super().__setitem__("HOME_TEAM_ELO", home_team_elo)
        super().__setitem__("AWAY_TEAM_ELO", away_team_elo)

        '''
        MAKE SURE THIS IS ADDED LAST
        '''
        super().__setitem__("HOME_TEAM_WINS", home_team_win)


    def hasSufficientData(self, home_team):
        number_of_games = home_team.getNumberGamesPlayed()

        if number_of_games > 10:
            sufficient_data = True
        else:
            sufficient_data = False

        return sufficient_data

    def _get_rankings(self, team_id, game_date):
        team_rankings = self._rankings.query(f'TEAM_ID == "{team_id}"').sort_values(by=['STANDINGSDATE'])
        team_rank_on_date = team_rankings.query(f'STANDINGSDATE == "{game_date}"')

        team_home_record = team_rank_on_date['HOME_RECORD'].iloc[0].split("-")
        team_home_wins, team_home_loses = map(int, team_home_record)

        team_road_record = team_rank_on_date['ROAD_RECORD'].iloc[0].split("-")
        team_road_wins, team_road_loses = map(int, team_road_record)
        return team_home_wins, team_home_loses, team_road_wins, team_road_loses
