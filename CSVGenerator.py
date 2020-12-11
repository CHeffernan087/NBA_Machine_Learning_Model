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
        self.generate_game_stats()

        rankings_frame = pd.read_csv("data/ranking.csv")
        teams = pd.read_csv("data/teams.csv")[['TEAM_ID', 'ABBREVIATION']]

        games_frame = pd.read_csv(f"data/game_stats/{self._year_to_generate}-{self._year_to_generate + 1}.csv")
        games_frame = games_frame[games_frame.date.str.contains(str(self._year_to_generate))]

        elo_frame = pd.read_csv("data/nba_elo.csv")
        elo_frame = elo_frame[elo_frame['date'].isin(games_frame['date'])]

        games_list = []
        team_stats = TeamStats(teams['TEAM_ID'])

        print("Generating data. This will take a minute....")
        num_rows = len(games_frame['date'])
        progress = 1
        ten_percent_data = int(num_rows / 10)
        next_progress_print = ten_percent_data
        for index, game_date in enumerate(games_frame['date']):
            home_team_id = games_frame['home_team_id'].iloc[index]
            away_team_id = games_frame['away_team_id'].iloc[index]

            home_team = team_stats.getTeam(home_team_id)
            away_team = team_stats.getTeam(away_team_id)
            home_team_win = games_frame['is_home_winner'].iloc[index]

            team_stats.recordGame({"HOME_TEAM": home_team_id, "AWAY_TEAM": away_team_id, "RESULT": home_team_win})

            home_team_abbreviation = teams[teams['TEAM_ID'] == home_team_id]['ABBREVIATION'].iloc[0]
            away_team_abbreviation = teams[teams['TEAM_ID'] == away_team_id]['ABBREVIATION'].iloc[0]

            current_game_elo = elo_frame[elo_frame['date'] == game_date]
            current_game_elo = current_game_elo[current_game_elo['team1'] == home_team_abbreviation]
            current_game_elo = current_game_elo[current_game_elo['team2'] == away_team_abbreviation]

            try:
                home_team_elo = current_game_elo['elo1_pre'].iloc[0]
                away_team_elo = current_game_elo['elo2_pre'].iloc[0]
                home_team_raptor = current_game_elo['raptor1_pre'].iloc[0]
                away_team_raptor = current_game_elo['raptor2_pre'].iloc[0]

                current_game = Game(home_team, away_team, game_date, rankings_frame, home_team_win, home_team_elo,
                                    away_team_elo, home_team_raptor, away_team_raptor)

                if current_game.hasSufficientData():
                    games_list.append(current_game)
            except IndexError:
                print(f"Game played on {game_date} between {home_team_abbreviation} and {away_team_abbreviation} "
                      f"not in elo dataset")

            # just for us so we can see the CSV being processed (its boring to wait)
            if index == next_progress_print:
                print(f"{progress * 10}%")
                progress += 1
                next_progress_print = ten_percent_data * progress

        game_writer = GameWriter(f"data/{self._year_to_generate}_games.csv", games_list)
        game_writer.write()

    def generate_game_stats(self):
        season_start_year = self._year_to_generate
        start_date = date.fromisoformat(f'{season_start_year}-10-01')
        if season_start_year == 2019:
            end_date = date.fromisoformat(f'{season_start_year + 1}-09-01')
        else:
            end_date = date.fromisoformat(f'{season_start_year + 1}-07-01')
        game_scraper = ScoreScraper(start_date, end_date)
        game_results = game_scraper.results_list

        output_file = f"data/game_stats/{season_start_year}-{season_start_year + 1}.csv"
        is_file_existing = Path(output_file).is_file()

        if is_file_existing:
            os.remove(output_file)

        with open(output_file, 'a') as output_csv:
            headers = game_results[0].keys()
            writer = csv.DictWriter(output_csv, fieldnames=headers, lineterminator='\n')
            writer.writeheader()
            for index, game_dict in enumerate(game_results):
                writer.writerow(game_dict)
