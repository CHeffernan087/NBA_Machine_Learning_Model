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
            print(f"Fetching data for: {date}")
            current_date_url = URL_TEMPLATE.format(month=date.month, day=date.day, year=date.year)
            response_data = requests.get(current_date_url)

            tree = html.fromstring(response_data.content)
            conference_standings = self.getConferenceStandings(tree)
            games_results_list = tree.xpath("//table[@class='teams']")
            for game_result_element in games_results_list:
                game_results_dict = {'date':str(date)}
                game_results_dict = self.get_teams_and_scores_dict(game_result_element,game_results_dict)
                updated_dictionary = self.get_team_record(games_results_list, conference_standings)
                self.results_list.append(game_results_dict)
            break;
    @staticmethod
    def date_range(start_date, end_date):
        for day_offset in range((end_date - start_date + timedelta(days=1)).days):
            yield start_date + timedelta(day_offset)

    def getTeamId(self,teamName):
        nameArray = teamName.split(" ")

        if (nameArray[0] == "Los"):
            franchise = f"LA {nameArray[2]}"
        elif (len(nameArray) > 2 and nameArray[0] != "Portland"):
            franchise = f"{nameArray[0]} {nameArray[1]}"
        else:
            franchise = nameArray[0]
        return self._team_name_to_id_dict[franchise]

    def getConferenceStandings(self,html_tree):
        conferenceStandings = {}
        for conference in ["E", "W"]:
            conf_standing = html_tree.xpath(f"//table[@id='confs_standings_{conference}']")[0]
            conf_rows = conf_standing.xpath(".//tr")

            for row in conf_rows:
                team_name = row.xpath(".//th/a")
                team_record = {}
                if (len(team_name) > 0):
                    team_name = team_name[0].text
                    team_id = self.getTeamId(team_name)
                    cellList = row.xpath(".//td")
                    team_record["team_name"] = team_name
                    team_record["wins"] =  cellList[0].text
                    team_record["loses"] = cellList[1].text
                    team_record["points_per_game"] = cellList[4].text
                    team_record["points_against_per_game"] = cellList[5].text
                    conferenceStandings[team_id] = team_record
        return conferenceStandings

    def get_team_record(self, team_score_dict, conference_standings):
        home_team = team_score_dict['home_team']
        home_team_id = team_score_dict['home_team_id']
        home_team_score = team_score_dict['home_team_score']
        away_team = team_score_dict['away_team']
        away_team_id = team_score_dict['away_team_id']
        away_team_score = team_score_dict['away_team_score']
        home_team_won = team_score_dict["is_home_winner"]

        # currently working on this
        home_team_record = conference_standings[home_team_id]

    def get_teams_and_scores_dict(self, game_result_element,team_score_dict):
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
