from collections import OrderedDict


class Game(OrderedDict):
    '''
    teams are a team object
    '''
    def __init__(self, home_team, away_team, game_date, rankings_dataframe, home_team_win):
        super().__init__()
        self._rankings = rankings_dataframe
        team_home_wins, team_home_loses, team_road_wins, team_road_loses = self._get_rankings(home_team.team_id, game_date)
        super().__setitem__("HOME_TEAM_HOME_WINS", team_home_wins)
        super().__setitem__("HOME_TEAM_HOME_LOSES", team_home_loses)
        super().__setitem__("HOME_TEAM_ROAD_WINS", team_road_wins)
        super().__setitem__("HOME_TEAM_ROAD_LOSES", team_road_loses)

        team_home_wins, team_home_loses, team_road_wins, team_road_loses = self._get_rankings(away_team.team_id, game_date)
        super().__setitem__("AWAY_TEAM_HOME_WINS", team_home_wins)
        super().__setitem__("AWAY_TEAM_HOME_LOSES", team_home_loses)
        super().__setitem__("AWAY_TEAM_ROAD_WINS", team_road_wins)
        super().__setitem__("AWAY_TEAM_ROAD_LOSES", team_road_loses)

        '''
        get the teams record of the last 3 games
        '''
        super().__setitem__("HOME_TEAM_FORM", home_team.getCurrentForm()[0])
        super().__setitem__("AWAY_TEAM_FORM", away_team.getCurrentForm()[0])

        '''
        MAKE SURE THIS IS ADDED LAST
        '''
        super().__setitem__("HOME_TEAM_WINS", home_team_win)

    def _get_rankings(self, team_id, game_date):
        team_rankings = self._rankings.query(f'TEAM_ID == "{team_id}"').sort_values(by=['STANDINGSDATE'])
        team_rank_on_date = team_rankings.query(f'STANDINGSDATE == "{game_date}"')

        team_home_record = team_rank_on_date['HOME_RECORD'].iloc[0].split("-")
        team_home_wins, team_home_loses = map(int, team_home_record)

        team_road_record = team_rank_on_date['ROAD_RECORD'].iloc[0].split("-")
        team_road_wins, team_road_loses = map(int, team_road_record)
        return team_home_wins, team_home_loses, team_road_wins, team_road_loses

    def hasSufficientData(self):
        team_home_wins = super().__getitem__("HOME_TEAM_HOME_WINS")
        team_home_loses = super().__getitem__("HOME_TEAM_HOME_LOSES")

        team_road_wins = super().__getitem__("HOME_TEAM_ROAD_WINS")
        team_road_loses = super().__getitem__("HOME_TEAM_ROAD_LOSES")

        homeGames = team_home_wins + team_home_loses
        awayGames = team_road_wins + team_road_loses
        numberOfGames = homeGames + awayGames

        if (numberOfGames > 10):
            sufficientData = True
        else:
            sufficientData = False
        return sufficientData

    def getResult(self):
        return [self.home_team, self.away_team, self.home_team_wins]
