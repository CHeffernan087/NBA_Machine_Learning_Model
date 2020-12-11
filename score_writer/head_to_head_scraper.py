import requests
from lxml import html
import csv
import os
from pathlib import Path
import json

with open("../Team/team_config.json") as team_config:
    team_name_to_id_dict = json.load(team_config)

PUPPETEER_URL_PREFIX = "http://localhost:3000?url="
URL_TEMPLATE = PUPPETEER_URL_PREFIX + "https://www.basketball-reference.com/leagues/NBA_{year}_standings.html#expanded_standings::none"

def getTeamIdFromAbbreviation(teamAbbreviation):
    if(teamAbbreviation == "Team"):
        return teamAbbreviation
    return team_name_to_id_dict[teamAbbreviation]


def getTeamId(teamName):
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
    columnHeadings = ["Team","ATL","BOS","BRK","CHI","CHO","CLE","DAL","DEN","DET","GSW","HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN","NOP","NYK","OKC","ORL","PHI","PHO","POR","SAC","SAS","TOR","UTA","WAS"]
    encodedColumnHeadings = []
    for heading in columnHeadings:
        encodedHeading = getTeamIdFromAbbreviation(heading)
        encodedColumnHeadings.append(encodedHeading)
    writer = csv.DictWriter(output_csv, fieldnames=encodedColumnHeadings, lineterminator='\n')
    writer.writeheader()

    current_date_url = URL_TEMPLATE.format(year=start_year)
    response_data = requests.get(current_date_url)
    tree = html.fromstring(response_data.content)
    headToHeadTable = tree.xpath('//*[@id="team_vs_team"]')
    tableRows = headToHeadTable[0].xpath('.//tr')
    tableRows = tableRows[2:len(tableRows)]
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




