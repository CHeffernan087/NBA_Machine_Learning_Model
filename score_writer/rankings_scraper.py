import argparse
import requests
from datetime import timedelta, datetime
from lxml import html
import csv
from time import sleep
from pathlib import Path

PUPPETEER_URL_PREFIX = "http://localhost:3000?url="
URL_TEMPLATE = PUPPETEER_URL_PREFIX + "https://www.basketball-reference.com/leagues/NBA_{year}_standings.html#expanded_standings::none"

def parseDate(date):
    return date.split("/")

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


def getCellValueInRow(row,data_stat):
    return row.xpath(f'td[@data-stat="{data_stat}"]')[0].text



start_year = int(input("Choose a year to get the standings for\n > "))
outputFile = f"{start_year}.csv"

is_file_existing = Path(outputFile).is_file()
with open(outputFile, 'a') as output_csv:
    fieldnames = ['TEAM_NAME', 'OVERALL', 'HOME_RECORD', 'ROAD_RECORD', 'POST_SEASON_RECORD', 'RECORD_CLOSE_GAMES', "RECORD_NORMAL_GAMES"]
    writer = csv.DictWriter(output_csv, fieldnames=fieldnames, lineterminator='\n')
    if not is_file_existing:
        writer.writeheader()

    current_date_url = URL_TEMPLATE.format(year=start_year)
    response_data = requests.get(current_date_url)
    tree = html.fromstring(response_data.content)
    seasonStandings = tree.xpath('//*[@id="expanded_standings"]')
    tableRows = seasonStandings[0].xpath('.//tr')
    tableRows = tableRows[2:len(tableRows)]
    for row in tableRows:
        test = row.xpath(f'td[@data-stat="team_name"]/a')
        team_name = row.xpath(f'td[@data-stat="team_name"]/a')[0].text
        overall = getCellValueInRow(row,"Overall")
        home_record = getCellValueInRow(row, "Home")
        road_record = getCellValueInRow(row,"Road")
        post_season_record = getCellValueInRow(row,"Post")
        record_close_games = getCellValueInRow(row,"3")
        record_normal_games = getCellValueInRow(row, "10")
        writer.writerow({'TEAM_NAME': team_name, 'OVERALL': overall, 'HOME_RECORD': home_record, 'ROAD_RECORD': road_record, "POST_SEASON_RECORD":post_season_record, "RECORD_CLOSE_GAMES":record_close_games, "RECORD_NORMAL_GAMES": record_normal_games})





