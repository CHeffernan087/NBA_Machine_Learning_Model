import csv
import os
from pathlib import Path


class GameWriter:
    def __init__(self, output_path, games_list):
        self.output_path = Path(output_path)
        self.games_list = games_list

    def write(self):
        headers = self.games_list[0].keys()
        file_exists = self.output_path.exists()
        if file_exists:
            # csv_writer.writeheader() may want to include when scraping
            os.remove(self.output_path)
        with self.output_path.open("a") as games_csv:
            csv_writer = csv.DictWriter(games_csv, fieldnames=headers, lineterminator='\n')
            csv_writer.writeheader()
            for game in self.games_list:
                csv_writer.writerow(game)
