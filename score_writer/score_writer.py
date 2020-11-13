import argparse
import requests
from datetime import timedelta, datetime
from lxml import html
import csv
from time import sleep
from pathlib import Path

URL_TEMPLATE = "https://www.basketball-reference.com/boxscores/?month={month}&day={day}&year={year}"


def date_range(start_date, end_date):
    for day_offset in range((end_date - start_date).days):
        yield start_date + timedelta(day_offset)


def get_winner_loser_score_dict(team_and_score_tree, is_winner=True):
    team_score_dict = {}
    finishing_place = team_and_score_tree.xpath(f".//tr[@class='{'winner' if is_winner else 'loser'}']/td/a/text()")
    team_score_dict["Team"] = finishing_place[0]
    score = team_and_score_tree.xpath(f".//tr[@class='{'winner' if is_winner else 'loser'}']/td[@class='right']/text()")
    team_score_dict["Score"] = score[0]
    return team_score_dict


def main(args):
    start_day, start_month, start_year = list(map(int, args.start.split("/")))
    end_day, end_month, end_year = list(map(int, args.end.split("/")))

    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)

    is_file_existing = Path(args.output_file).is_file()
    with open(args.output_file, 'a') as output_csv:
        fieldnames = ['Winner', 'Winner_score', 'Loser', 'Loser_score', 'Date']
        writer = csv.DictWriter(output_csv, fieldnames=fieldnames, lineterminator='\n')
        if not is_file_existing:
            writer.writeheader()

        for date in date_range(start_date, end_date):
            current_date_url = URL_TEMPLATE.format(month=date.month, day=date.day, year=date.year)
            response_data = requests.get(current_date_url)
            sleep(1)
            tree = html.fromstring(response_data.content)
            teams_and_scores_list = tree.xpath("//table[@class='teams']")
            for team_and_score in teams_and_scores_list:
                loser_score_dict = get_winner_loser_score_dict(team_and_score, is_winner=False)
                winner_score_dict = get_winner_loser_score_dict(team_and_score)

                writer.writerow({'Winner': winner_score_dict['Team'], 'Winner_score': winner_score_dict['Score'],
                                 'Loser': loser_score_dict['Team'], 'Loser_score': loser_score_dict['Score'],
                                 'Date': date})


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--start", type=str, help="inclusive start date to begin gathering scores DD/MM/YYYY",
                        required=True)
    parser.add_argument("-e", "--end", type=str, help="exclusive end date to stop gathering scores DD/MM/YYYY",
                        required=True)
    parser.add_argument("-o", "--output_file", type=str, help="output path for csv file", required=False,
                        default="scores.csv")
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
