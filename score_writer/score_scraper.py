from datetime import timedelta, datetime
from time import sleep
import json

import requests
from lxml import html

URL_TEMPLATE = "https://www.basketball-reference.com/boxscores/?month={month}&day={day}&year={year}"


class ScoreScraper:

    def __init__(self, start_date: datetime, end_date: datetime = None) -> None:
        self._start_date = start_date
        self._end_date = start_date if end_date is None else end_date
        self.results_list = []
        with open("Team/team_config.json") as team_config:
            self._team_name_to_id_dict = json.load(team_config)

        for date in ScoreScraper.date_range(self._start_date, self._end_date):
            current_date_url = URL_TEMPLATE.format(month=date.month, day=date.day, year=date.year)
            response_data = requests.get(current_date_url)
            sleep(1)
            tree = html.fromstring(response_data.content)
            games_results_list = tree.xpath("//table[@class='teams']")
            for game_result_element in games_results_list:
                game_results_dict = self.get_teams_and_scores_dict(game_result_element)
                game_results_dict['date'] = str(date.date())
                self.results_list.append(game_results_dict)

    @staticmethod
    def date_range(start_date, end_date):
        for day_offset in range((end_date - start_date + timedelta(days=1)).days):
            yield start_date + timedelta(day_offset)

    def get_teams_and_scores_dict(self, game_result_element):
        team_score_dict = {}
        winner_loser_order = game_result_element.xpath(".//tr[@class='winner' or @class='loser']")
        is_home_winner = winner_loser_order[1].attrib['class'] == 'winner'

        team_score_dict["is_home_winner"] = is_home_winner

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