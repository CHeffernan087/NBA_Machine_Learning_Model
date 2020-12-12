from datetime import timedelta, datetime
from time import sleep
import json
from Team.TeamStats import TeamStats

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

        team_stats = TeamStats(range(1, 31))
        for date in ScoreScraper.date_range(self._start_date, self._end_date):
            print(f"Fetching data for: {date}")
            current_date_url = URL_TEMPLATE.format(month=date.month, day=date.day, year=date.year)
            response_data = requests.get(current_date_url)

            tree = html.fromstring(response_data.content)
            games_results_list = tree.xpath("//table[@class='teams']")

            for game_result_element in games_results_list:

                game_results_dict = {'date':str(date)}
                game_results_dict = self.get_teams_and_scores_dict(game_result_element,game_results_dict)
                game_result = self.get_game_result(game_result_element)
                '''_______________________'''
                home_team = team_stats.getTeam(game_results_dict["home_team_id"])
                away_team = team_stats.getTeam(game_results_dict["away_team_id"])
                self.get_home_and_road_record(game_results_dict, home_team, away_team)


                '''_______________________'''

                self.get_win_loss_stats(game_results_dict, home_team, away_team)
                game_results_dict["is_home_winner"] = game_result
                # we record the games as we go so that we can manually compute features about the teams before the game such as
                # home record, road record etc
                team_stats.recordGame( [game_results_dict["home_team_id"], game_results_dict["away_team_id"], game_results_dict["is_home_winner"],game_results_dict['home_team_score'] , game_results_dict['away_team_score'] ])
                self.results_list.append(game_results_dict)

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

    def getConferenceStandings(self,html_tree):
        conferenceStandings = {}
        for conference in ["E", "W"]:
            games_played_today = len(html_tree.xpath(f"//table[@id='confs_standings_{conference}']")) > 0
            if(games_played_today):
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
                        team_record["wins"] =  int(cellList[0].text)
                        team_record["loses"] = int(cellList[1].text)
                        team_record["points_per_game"] = float(cellList[4].text)
                        team_record["points_against_per_game"] = float(cellList[5].text)
                        conferenceStandings[team_id] = team_record

        return conferenceStandings

    def get_win_loss_stats(self, team_score_dict,home_team, away_team):
        team_score_dict["home_team_wins"] = home_team.getWins()
        team_score_dict["home_team_loses"] = home_team.getLoses()
        team_score_dict["home_team_points_per_game"] = home_team.getPointsPerGame()
        team_score_dict["home_team_points_against_per_game"] = home_team.getPointsConcededPerGame()
        team_score_dict["away_team_wins"] = away_team.getWins()
        team_score_dict["away_team_loses"] = away_team.getLoses()
        team_score_dict["away_team_points_per_game"] = away_team.getPointsPerGame()
        team_score_dict["away_team_points_against_per_game"] = away_team.getPointsConcededPerGame()
    '''
    The standings data scraped is updated with the result 
    so we need to decrement the stats to adjust for this
    '''
    def add_team_record_to_dict(self, team_score_dict, conference_standings, game_result):
        home_team_id = team_score_dict['home_team_id']
        home_team_score = team_score_dict['home_team_score']
        away_team_id = team_score_dict['away_team_id']
        away_team_score = team_score_dict['away_team_score']
        home_team_won = game_result

        home_team_record = conference_standings[home_team_id]
        away_team_record = conference_standings[away_team_id]

        home_team_games_played  = home_team_record["wins"] + home_team_record["loses"]
        away_team_games_played = away_team_record["wins"] + away_team_record["loses"]


        if home_team_won == 1:
            home_team_record["wins"] = home_team_record["wins"] - 1
            away_team_record["loses"] = away_team_record["loses"] - 1
        else:
            home_team_record["loses"] = home_team_record["loses"] - 1
            away_team_record["wins"] = away_team_record["wins"] -1

        home_team_record["points_per_game"] = 0 if home_team_games_played ==1 else  ((home_team_record["points_per_game"] * home_team_games_played) - home_team_score) / home_team_games_played - 1
        home_team_record["points_against_per_game"] = 0 if home_team_games_played ==1 else  ((home_team_record["points_against_per_game"] * home_team_games_played) - away_team_score) / home_team_games_played - 1
        away_team_record["points_per_game"] = 0 if away_team_games_played ==1 else ((away_team_record["points_per_game"] * away_team_games_played) - away_team_score) / away_team_games_played - 1
        away_team_record["points_against_per_game"] = 0 if away_team_games_played == 1 else ((away_team_record["points_against_per_game"] * away_team_games_played) - home_team_score) / away_team_games_played - 1

        team_score_dict["home_team_wins"] = home_team_record["wins"]
        team_score_dict["home_team_loses"] = home_team_record["loses"]
        team_score_dict["home_team_points_per_game"] = home_team_record["points_per_game"]
        team_score_dict["home_team_points_against_per_game"] = home_team_record["points_against_per_game"]
        team_score_dict["away_team_wins"] = away_team_record["wins"]
        team_score_dict["away_team_loses"] = away_team_record["loses"]
        team_score_dict["away_team_points_per_game"] = away_team_record["points_per_game"]
        team_score_dict["away_team_points_against_per_game"] = away_team_record["points_against_per_game"]

        return team_score_dict

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
        return team_score_dict

    def get_game_result(self,game_result_element):
        winner_loser_order = game_result_element.xpath(".//tr[@class='winner' or @class='loser']")
        is_home_winner = winner_loser_order[1].attrib['class'] == 'winner'
        return 1 if is_home_winner else 0