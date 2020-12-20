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

    def generate(self, data_frame=None, output_location=None , append = False):

        teams = pd.read_csv("data/teams.csv")[['TEAM_ID', 'ABBREVIATION']]
        filepath = f"data/game_stats/{self._year_to_generate}-{self._year_to_generate + 1}.csv"

        data_frame_defined = data_frame is not None
        games_frame = data_frame if data_frame_defined else pd.read_csv(filepath)

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

            home_team_points = games_frame['home_team_score'].iloc[index]
            away_team_points = games_frame['away_team_score'].iloc[index]

            # get the elo stats from the CSV
            home_team_elo = games_frame['home_team_elo'].iloc[index]
            away_team_elo = games_frame['away_team_elo'].iloc[index]
            home_team_raptor = games_frame['home_team_raptor'].iloc[index]
            away_team_raptor = games_frame['away_team_raptor'].iloc[index]

            home_team_hth_record= games_frame['home_team_hth_record'].iloc[index]
            away_team_hth_record = games_frame['away_team_hth_record'].iloc[index]

            current_game = Game(home_team, away_team, home_team_win, home_team_elo,
                                away_team_elo, home_team_raptor, away_team_raptor, home_team_hth_record, away_team_hth_record)


            games_list.append(current_game)

            team_stats.recordGame({"HOME_TEAM": home_team_id, "AWAY_TEAM": away_team_id, "RESULT": home_team_win, "HOME_TEAM_POINTS": home_team_points,
                 "AWAY_TEAM_POINTS": away_team_points})
            # just for us so we can see the CSV being processed (its boring to wait)
            if index == next_progress_print:
                print(f"{progress * 10}%")
                progress += 1
                next_progress_print = ten_percent_data * progress
        output_file_name = output_location if output_location !=None else f"data/{self._year_to_generate}_games.csv"
        game_writer = GameWriter(output_file_name, games_list, append)
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


    def scrapeAllTrainingData(self, yearsToScrape = [2015,2016,2017,2018]):
        for year in yearsToScrape:
            self.generate_game_stats(year, shouldOverwriteCSV=True)
        self.stitchLocalCsvs(yearsToScrape)

    def stitchLocalCsvs(self, yearsToScrape = [2015,2016,2017,2018]):
        outputFileName = f"data/training_data/training_data_{yearsToScrape[0]}-{yearsToScrape[len(yearsToScrape)-1]}.csv"
        output_file = open(outputFileName, "w")
        for index,year in enumerate(yearsToScrape):
            current_csv = pd.read_csv(f"data/game_stats/{year}-{year + 1}.csv")
            if(index == 0 ):
                headers = current_csv.head()
                writer = csv.DictWriter(output_file, fieldnames=headers)
                writer.writeheader()
                output_file.close()

            current_csv.to_csv(f'{outputFileName}', mode='a', header=False, index=False)

    def generate_multiple_years(self,years_to_generate = [2015,2016,2017,2018] ):
        self.stitchLocalCsvs(yearsToScrape = years_to_generate)
        filepath = f"data/training_data/training_data_{years_to_generate[0]}-{years_to_generate[-1]}.csv"
        outputFileName = f"data/training_features/training_features_{years_to_generate[0]}-{years_to_generate[-1]}.csv"
        os.remove(outputFileName)
        games_frame = pd.read_csv(filepath)
        for year in years_to_generate:
            self._year_to_generate = year
            current_frame = games_frame.query(f"season_id == {year}")
            self.generate(data_frame= current_frame,output_location=outputFileName, append=True )

        print("Finished generating the training features")




