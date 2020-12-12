import json
from Team.TeamStats import TeamStats
from datetime import timedelta, datetime, date
from typing import Union

import requests
from lxml import html

from Team.Team import Team

URL_TEMPLATE = "https://www.basketball-reference.com/boxscores/?month={month}&day={day}&year={year}"


class ScoreScraper:

    def __init__(self, start_date: Union[datetime, date], end_date: Union[datetime, date] = None) -> None:
        self._start_date = start_date
        self._end_date = start_date if end_date is None else end_date
        self.results_list = []
        with open("Team/team_config.json") as team_config:
            self._team_name_to_id_dict = json.load(team_config)
            teams = self._team_name_to_id_dict.values()
        team_stats = TeamStats(teams)
        for scrape_date in ScoreScraper.date_range(self._start_date, self._end_date):
            print(f"Fetching data for: {scrape_date}")
            current_date_url = URL_TEMPLATE.format(month=scrape_date.month, day=scrape_date.day, year=scrape_date.year)
            response_data = requests.get(current_date_url)

            tree = html.fromstring(response_data.content)
            games_results_list = tree.xpath("//table[@class='teams']")

            for game_result_element in games_results_list:

                game_results_dict = {'date':str(scrape_date)}
                game_results_dict = self.get_teams_and_scores_dict(game_result_element,game_results_dict)
                game_result = self.get_game_result(game_result_element)

                home_team = team_stats.getTeam(game_results_dict["home_team_id"])
                away_team = team_stats.getTeam(game_results_dict["away_team_id"])
                self.get_home_and_road_record(game_results_dict, home_team, away_team)

                self.get_win_loss_stats(game_results_dict, home_team, away_team)
                game_results_dict["is_home_winner"] = game_result

                # record the game to compute stats on the fly
                team_stats.recordGame( {"HOME_TEAM":game_results_dict["home_team_id"], "AWAY_TEAM":game_results_dict["away_team_id"], "RESULT":game_results_dict["is_home_winner"],"HOME_TEAM_POINTS":game_results_dict['home_team_score'] , "AWAY_TEAM_POINTS":game_results_dict['away_team_score'] })
                self.results_list.append(game_results_dict)

    @staticmethod
    def date_range(start_date, end_date):
        for day_offset in range((end_date - start_date + timedelta(days=1)).days):
            yield start_date + timedelta(day_offset)

    def getTeamId(self, team_name):
        franchise = Team.get_franchise(team_name)
        return self._team_name_to_id_dict[franchise]

    def get_home_and_road_record(self, game_results_dict, home_team, away_team):
        home_team_record = home_team.getTeamRecord()
        away_team_record = away_team.getTeamRecord()
        game_results_dict["home_team_home_wins"] = home_team_record["HOME_WINS"]
        game_results_dict["home_team_home_loses"] = home_team_record["HOME_LOSES"]
        game_results_dict["home_team_road_wins"] = home_team_record["AWAY_WINS"]
        game_results_dict["home_team_road_loses"] = home_team_record["AWAY_LOSES"]
        game_results_dict["away_team_home_wins"] = away_team_record["HOME_WINS"]
        game_results_dict["away_team_home_loses"] = away_team_record["HOME_LOSES"]
        game_results_dict["away_team_road_wins"] = away_team_record["AWAY_WINS"]
        game_results_dict["away_team_road_loses"] = away_team_record["AWAY_LOSES"]


    def get_win_loss_stats(self, team_score_dict,home_team, away_team):
        team_score_dict["home_team_wins"] = home_team.getWins()
        team_score_dict["home_team_loses"] = home_team.getLoses()
        team_score_dict["home_team_points_per_game"] = home_team.getPointsPerGame()
        team_score_dict["home_team_points_against_per_game"] = home_team.getPointsConcededPerGame()
        team_score_dict["away_team_wins"] = away_team.getWins()
        team_score_dict["away_team_loses"] = away_team.getLoses()
        team_score_dict["away_team_points_per_game"] = away_team.getPointsPerGame()
        team_score_dict["away_team_points_against_per_game"] = away_team.getPointsConcededPerGame()


    @staticmethod
    def add_ppg_to_record(team_record, games_played, team_score, other_team_score):
        if games_played == 1:
            team_record["points_per_game"] = 0
            team_record["points_against_per_game"] = 0
        else:
            team_record["points_per_game"] = ((team_record["points_per_game"] * games_played) -
                                              team_score) / games_played - 1
            team_record["points_against_per_game"] = ((team_record["points_against_per_game"] * games_played) -
                                                      other_team_score) / games_played - 1
        return team_record

    def get_teams_and_scores_dict(self, game_result_element, team_score_dict):
        winner_loser_order = game_result_element.xpath(".//tr[@class='winner' or @class='loser']")
        is_home_winner = winner_loser_order[1].attrib['class'] == 'winner'

        winning_team = str(game_result_element.xpath(f".//tr[@class='winner']/td/a/text()")[0])
        losing_team = str(game_result_element.xpath(f".//tr[@class='loser']/td/a/text()")[0])
        winning_score = int(game_result_element.xpath(f".//tr[@class='winner']/td[@class='right']/text()")[0])
        losing_score = int(game_result_element.xpath(f".//tr[@class='loser']/td[@class='right']/text()")[0])

        home_team = winning_team if is_home_winner else losing_team
        away_team = losing_team if is_home_winner else winning_team

        team_score_dict['home_team'] = home_team
        team_score_dict['home_team_id'] = self._team_name_to_id_dict[home_team]
        team_score_dict['home_team_score'] = winning_score if is_home_winner else losing_score
        team_score_dict['away_team'] = away_team
        team_score_dict['away_team_id'] = self._team_name_to_id_dict[away_team]
        team_score_dict['away_team_score'] = losing_score if is_home_winner else winning_score
        return team_score_dict

    def get_game_result(self,game_result_element):
        winner_loser_order = game_result_element.xpath(".//tr[@class='winner' or @class='loser']")
        is_home_winner = winner_loser_order[1].attrib['class'] == 'winner'
        return 1 if is_home_winner else 0