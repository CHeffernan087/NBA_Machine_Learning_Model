import csv
import json
import os
from pathlib import Path
from Team.Team import Team
import requests
from lxml import html
'''
We thought a teams performance in a previous season might be a good indicator of how well 
they will do this season. E.g if youre the reigning champion its unlikely that youre going 
to lose to the team that came in last place the previous year 
'''
with open("../Team/team_config.json") as team_config:
    team_name_to_id_dict = json.load(team_config)

# The page we were trying to scrape was rendered using Javascript so it was necessary to proxy the request through a
# node server to render the JS and return the result.

PUPPETEER_URL_PREFIX = "http://localhost:3000?url="
URL_TEMPLATE = PUPPETEER_URL_PREFIX + "https://www.basketball-reference.com/leagues/NBA_{year}_standings.html#expanded_standings::none"


def getCellValueInRow(row, data_stat):
    """
    Helper function to extract a particular datum from a string representing a row in a HTML table
    :param row: A string representing a row in a html table
    :param data_stat: the particular cell in the row that you would like to extract (each cell has an ID based on its column heading)
    :return: the text contained within the cell specified
    """
    return row.xpath(f'td[@data-stat="{data_stat}"]')[0].text


def getTeamId(team_name):
    '''
    :param team_name: The English name of a team e.g "Chicago Bulls"
    :return: the integer ID representation of that team per team_config.json
    '''
    franchise = Team.get_franchise(team_name)
    return team_name_to_id_dict[franchise]


start_year = int(input("Choose a year to get the standings for\n > "))
outputFile = f"../data/season_rankings/{start_year}.csv"

is_file_existing = Path(outputFile).is_file()

if is_file_existing:
    os.remove(outputFile)

# get the rankings for a given season, extact the rows, extract the data that we want from the cells and
# add to a dictionary
with open(outputFile, 'a') as output_csv:
    fieldnames = ['TEAM_ID', 'TEAM_NAME', 'OVERALL', 'HOME_RECORD', 'ROAD_RECORD', 'POST_SEASON_RECORD',
                  'RECORD_CLOSE_GAMES', "RECORD_NORMAL_GAMES"]
    writer = csv.DictWriter(output_csv, fieldnames=fieldnames, lineterminator='\n')
    writer.writeheader()

    # Fetch the data from basketballreference.com
    current_date_url = URL_TEMPLATE.format(year=start_year)
    response_data = requests.get(current_date_url)
    tree = html.fromstring(response_data.content)
    seasonStandings = tree.xpath('//*[@id="expanded_standings"]')

    # extract the tables and rows from the HTML string
    tableRows = seasonStandings[0].xpath('.//tr')
    tableRows = tableRows[2:len(tableRows)]

    # iterate over the rows and extract data from specific cells in the row
    for row in tableRows:
        rankCell = row.xpath(f'th[@data-stat="ranker"]')
        row_has_data = len(rankCell) > 0
        if row_has_data and rankCell[0].text != "Rk":
            team_name = row.xpath(f'td[@data-stat="team_name"]/a')[0].text
            team_id = getTeamId(team_name)
            overall = getCellValueInRow(row, "Overall")
            home_record = getCellValueInRow(row, "Home")
            road_record = getCellValueInRow(row, "Road")
            post_season_record = getCellValueInRow(row, "Post")
            record_close_games = getCellValueInRow(row, "3")
            record_normal_games = getCellValueInRow(row, "10")
            writer.writerow({'TEAM_ID': team_id, 'TEAM_NAME': team_name, 'OVERALL': overall, 'HOME_RECORD': home_record,
                             'ROAD_RECORD': road_record, "POST_SEASON_RECORD": post_season_record,
                             "RECORD_CLOSE_GAMES": record_close_games, "RECORD_NORMAL_GAMES": record_normal_games})
