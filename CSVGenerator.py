import csv
import os
from datetime import date
from pathlib import Path

import pandas as pd

from Team.TeamStats import TeamStats
from score_writer.game import Game
from score_writer.game_writer import GameWriter
from score_writer.score_scraper import ScoreScraper


class CSVGenerator:
    def __init__(self, year_to_generate):
        self._year_to_generate = year_to_generate

    def generate(self):

        teams = pd.read_csv("data/teams.csv")[['TEAM_ID', 'ABBREVIATION']]

        games_frame = pd.read_csv(f"data/game_stats/{self._year_to_generate}-{self._year_to_generate + 1}.csv")
        games_frame = games_frame[games_frame.date.str.contains(str(self._year_to_generate))]

        games_list = []
        team_stats = TeamStats(teams['TEAM_ID'], self._year_to_generate)

        print("Generating data. This will take a minute....")
        num_rows = len(games_frame['date'])
        progress = 1
        ten_percent_data = int(num_rows / 10)
        next_progress_print = ten_percent_data
        for index, game_date in enumerate(games_frame['date']):
            home_team_id = games_frame['home_team_id'].iloc[index]
            away_team_id = games_frame['away_team_id'].iloc[index]

            # get the Team objects for the two teams in the game
            home_team = team_stats.getTeam(home_team_id)
            away_team = team_stats.getTeam(away_team_id)
            home_team_win = games_frame['is_home_winner'].iloc[index]

            # get the elo stats from the CSV
            home_team_elo = games_frame['home_team_elo'].iloc[index]
            away_team_elo = games_frame['away_team_elo'].iloc[index]
            home_team_raptor = games_frame['home_team_raptor'].iloc[index]
            away_team_raptor = games_frame['away_team_raptor'].iloc[index]

            home_team_hth_record= games_frame['home_team_hth_record'].iloc[index]
            away_team_hth_record = games_frame['away_team_hth_record'].iloc[index]

            current_game = Game(home_team, away_team, home_team_win, home_team_elo,
                                away_team_elo, home_team_raptor, away_team_raptor, home_team_hth_record, away_team_hth_record)

            if current_game.hasSufficientData(home_team):
                games_list.append(current_game)

            team_stats.recordGame({"HOME_TEAM": home_team_id, "AWAY_TEAM": away_team_id, "RESULT": home_team_win, "HOME_TEAM_POINTS": 0,
                 "AWAY_TEAM_POINTS": 0})
            # just for us so we can see the CSV being processed (its boring to wait)
            if index == next_progress_print:
                print(f"{progress * 10}%")
                progress += 1
                next_progress_print = ten_percent_data * progress

        game_writer = GameWriter(f"data/{self._year_to_generate}_games.csv", games_list)
        game_writer.write()

    def generate_game_stats(self, year_to_generate=None, output_file_name = None, shouldOverwriteCSV = True):

        season_start_year = self._year_to_generate if year_to_generate == None else year_to_generate
        start_date = date.fromisoformat(f'{season_start_year}-10-01')
        if(season_start_year==2019):
            end_date = date.fromisoformat(f'{season_start_year+1}-10-21')
        else:
            end_date = date.fromisoformat(f'{season_start_year+1}-07-01')

        gameScraper = ScoreScraper(start_date, end_date)
        game_results = gameScraper.results_list
        # for game in game_results:

        outputFile = f"data/game_stats/{season_start_year}-{season_start_year+1}.csv" if output_file_name == None else output_file_name
        is_file_existing = Path(outputFile).is_file()

        if (is_file_existing and shouldOverwriteCSV):
            os.remove(outputFile)

        with open(outputFile, 'a') as output_csv:
            '''
            iterate over all the games scraped by the programme
            '''
            for index, game_dict in enumerate(game_results):
                if index == 0 :
                    headers = game_dict.keys()
                    writer = csv.DictWriter(output_csv, fieldnames=headers, lineterminator='\n')
                    writer.writeheader()
                writer.writerow(game_dict)


    def scrapeAllTrainingData(self, yearsToScrape = [2016,2017,2018,2019]):
        outputFileName = f"data/training_data/training_data_{yearsToScrape[0]}-{yearsToScrape[len(yearsToScrape)-1]}.csv"
        for year in yearsToScrape:
            self.generate_game_stats(year,outputFileName, shouldOverwriteCSV=False)
