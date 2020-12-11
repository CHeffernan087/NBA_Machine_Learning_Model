import json
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

        for scrape_date in ScoreScraper.date_range(self._start_date, self._end_date):
            print(f"Fetching data for: {scrape_date}")
            current_date_url = URL_TEMPLATE.format(month=scrape_date.month, day=scrape_date.day, year=scrape_date.year)
            response_data = requests.get(current_date_url)

            tree = html.fromstring(response_data.content)
            conference_standings = self.getConferenceStandings(tree)
            games_results_list = tree.xpath("//table[@class='teams']")
            for game_result_element in games_results_list:
                game_results_dict = {'date': str(scrape_date)}
                game_results_dict = self.get_teams_and_scores_dict(game_result_element, game_results_dict)
                game_results_dict = self.add_team_record_to_dict(game_results_dict, conference_standings)
                self.results_list.append(game_results_dict)

    @staticmethod
    def date_range(start_date, end_date):
        for day_offset in range((end_date - start_date + timedelta(days=1)).days):
            yield start_date + timedelta(day_offset)

    def getTeamId(self, team_name):
        franchise = Team.get_franchise(team_name)
        return self._team_name_to_id_dict[franchise]

    def getConferenceStandings(self, html_tree):
        conference_standings = {}
        for conference in ["E", "W"]:
            games_played_today = len(html_tree.xpath(f"//table[@id='confs_standings_{conference}']")) > 0
            if games_played_today:
                conf_standing = html_tree.xpath(f"//table[@id='confs_standings_{conference}']")[0]
                conf_rows = conf_standing.xpath(".//tr")

                for row in conf_rows:
                    team_name = row.xpath(".//th/a")
                    team_record = {}
                    if len(team_name) > 0:
                        team_name = team_name[0].text
                        team_id = self.getTeamId(team_name)
                        cell_list = row.xpath(".//td")
                        team_record["team_name"] = team_name
                        team_record["wins"] = int(cell_list[0].text)
                        team_record["loses"] = int(cell_list[1].text)
                        team_record["points_per_game"] = float(cell_list[4].text)
                        team_record["points_against_per_game"] = float(cell_list[5].text)
                        conference_standings[team_id] = team_record
        return conference_standings

    '''
    The standings data scraped is updated with the result 
    so we need to decrement the stats to adjust for this
    '''

    @staticmethod
    def add_team_record_to_dict(team_score_dict, conference_standings):
        home_team_id = team_score_dict['home_team_id']
        home_team_score = team_score_dict['home_team_score']
        away_team_id = team_score_dict['away_team_id']
        away_team_score = team_score_dict['away_team_score']
        home_team_won = team_score_dict["is_home_winner"]

        home_team_record = conference_standings[home_team_id]
        away_team_record = conference_standings[away_team_id]

        home_team_games_played = home_team_record["wins"] + home_team_record["loses"]
        away_team_games_played = away_team_record["wins"] + away_team_record["loses"]

        if home_team_won == 1:
            home_team_record["wins"] -= 1
            away_team_record["loses"] -= 1
        else:
            home_team_record["loses"] -= 1
            away_team_record["wins"] -= 1

        home_team_record = ScoreScraper.add_ppg_to_record(home_team_record, home_team_games_played, home_team_score,
                                                          away_team_score)

        away_team_record = ScoreScraper.add_ppg_to_record(away_team_record, away_team_games_played, away_team_score,
                                                          home_team_score)

        team_score_dict["home_team_wins"] = home_team_record["wins"]
        team_score_dict["home_team_loses"] = home_team_record["loses"]
        team_score_dict["home_team_points_per_game"] = home_team_record["points_per_game"]
        team_score_dict["home_team_points_against_per_game"] = home_team_record["points_against_per_game"]
        team_score_dict["away_team_wins"] = away_team_record["wins"]
        team_score_dict["away_team_loses"] = away_team_record["loses"]
        team_score_dict["away_team_points_per_game"] = away_team_record["points_per_game"]
        team_score_dict["away_team_points_against_per_game"] = away_team_record["points_against_per_game"]

        return team_score_dict

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
        team_score_dict["is_home_winner"] = 1 if is_home_winner else 0
        return team_score_dict
