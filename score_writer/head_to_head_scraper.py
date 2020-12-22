import requests
from lxml import html
import csv
import os
from pathlib import Path
import json

'''
We had an idea that Team A's performance in the last year against Team B 
might give us an indication as to which team will win this time. E.g if Team A
won the last 4 games that they played against Team B then it is likely that they 
will win the next game that they play against TeamB. With this assumption we wrote 
this scraper to extract this data from basketballreference.com
'''
with open("../Team/team_config.json") as team_config:
    team_name_to_id_dict = json.load(team_config)

# The page we were trying to scrape was rendered using Javascript so it was necessary to proxy the request through a
# node server to render the JS and return the result.

PUPPETEER_URL_PREFIX = "http://localhost:3000?url="
URL_TEMPLATE = PUPPETEER_URL_PREFIX + "https://www.basketball-reference.com/leagues/NBA_{year}_standings.html#expanded_standings::none"

def getTeamIdFromAbbreviation(teamAbbreviation):
    '''
    :param teamAbbreviation: The Abbreviation of a team (CHI)
    :return: The ID associated with the team per team_config.json
    '''
    if(teamAbbreviation == "Team"):
        return teamAbbreviation
    return team_name_to_id_dict[teamAbbreviation]

def getTeamId(teamName):
    '''
    :param teamName: the English name of the team e.g Chicago Bulls
    :return: The ID associated with the team per team_config.json
    '''
    nameArray = teamName.split(" ")

    if(nameArray[0] == "Los"):
        franchise =  f"LA {nameArray[2]}"
    elif(len(nameArray) > 2 and nameArray[0] != "Portland"):
        franchise = f"{nameArray[0]} {nameArray[1]}"
    else:
        franchise = nameArray[0]
    return team_name_to_id_dict[franchise]


start_year = int(input("Choose a year to get the head to head data for\n > "))
outputFile = f"../data/head_to_head/{start_year}.csv"

is_file_existing = Path(outputFile).is_file()

if(is_file_existing):
    os.remove(outputFile)

with open(outputFile, 'a') as output_csv:
    # fetch the data about a particular year
    current_date_url = URL_TEMPLATE.format(year=start_year)
    response_data = requests.get(current_date_url)
    tree = html.fromstring(response_data.content)

    # using XPaths extract table headings and rows from the table we want
    headToHeadTable = tree.xpath('//*[@id="team_vs_team"]')
    tableRows = headToHeadTable[0].xpath('.//tr')
    table_headings = tableRows[0].xpath('.//th')[1:]

    # Taking the headings from the table and add them to a dict. This is all the team names abbreviated e.g CHI - Chicago Bulls
    columnHeadings = [heading.text for heading in table_headings]
    encodedColumnHeadings = []
    for heading in columnHeadings:
        encodedHeading = getTeamIdFromAbbreviation(heading)
        encodedColumnHeadings.append(encodedHeading)
    writer = csv.DictWriter(output_csv, fieldnames=encodedColumnHeadings, lineterminator='\n')
    writer.writeheader()

    # iterate over all the rows in the table and extract the head to head matrix that we want e.g
    '''
       A  B
    A  -  0-2
    B  2-0 -
    '''
    tableRows = tableRows[1:len(tableRows)]
    for row in tableRows:
        rankCell = row.xpath(f'th[@data-stat="ranker"]')
        row_has_data = len(rankCell) > 0
        if(row_has_data and rankCell[0].text != "Rk"):
            data_cells = row.xpath("td")
            teamCell = data_cells[0]
            teamName = teamCell.xpath("a")[0].text
            outputDict = {"Team":getTeamId(teamName)}
            for index , data_cells in enumerate(data_cells):
                if(index > 0):
                    outputDict[encodedColumnHeadings[index]] = data_cells.text
            writer.writerow(outputDict)




