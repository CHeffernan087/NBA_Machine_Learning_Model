import csv
import os
from pathlib import Path


class GameWriter:
    def __init__(self, output_path, games_list, append=False):
        self.output_path = Path(output_path)
        self.games_list = games_list
        self.should_append_to_file = append

    def write(self):
        headers = self.games_list[0].keys()
        file_exists = self.output_path.exists()
        if file_exists and not self.should_append_to_file:
            os.remove(self.output_path)
        with self.output_path.open("a") as games_csv:
            csv_writer = csv.DictWriter(games_csv, fieldnames=headers, lineterminator='\n')
            if not file_exists:
                csv_writer.writeheader()
            for game in self.games_list:
                csv_writer.writerow(game)
