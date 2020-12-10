import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from score_writer.game import Game
from score_writer.game_writer import GameWriter
from Team.TeamStats import TeamStats


def parseInput(input):
    input = input.lower()[0]
    if input == "y":
        return True
    return False


YEAR_TO_GENERATE = 2020

FILE_PATH = f"data/{YEAR_TO_GENERATE}_games.csv"

userInput = input("Do you want to generate CSV? (y/n)\n> ")
shouldGenCsv = parseInput(userInput)

# ---------- (UN)COMMENT THIS TO MAKE CSV FILE / APPEND TO EXISTING CSV ----------------
if shouldGenCsv:
    rankings_frame = pd.read_csv("data/ranking.csv")
    teams = pd.read_csv("data/teams.csv")['TEAM_ID']

    games_frame = pd.read_csv("data/games.csv")
    games_frame = games_frame[games_frame.GAME_DATE_EST.str.contains(str(YEAR_TO_GENERATE))]

    elo_frame = pd.read_csv("data/nba_elo.csv")
    elo_frame = elo_frame[elo_frame['date'].isin(games_frame['GAME_DATE_EST'])]

    games_list = []
    team_stats = TeamStats(teams)

    print("Generating data. This will take a minute....")
    num_rows = num_columns = len(games_frame['GAME_DATE_EST'])
    progress = 1
    tenPercentData = int(num_rows / 10)
    nextProgressPrint = tenPercentData
    for index, game_date in enumerate(games_frame['GAME_DATE_EST']):
        home_team_id = games_frame['HOME_TEAM_ID'].iloc[index]
        away_team_id = games_frame['VISITOR_TEAM_ID'].iloc[index]
        home_team = team_stats.getTeam(home_team_id)
        away_team = team_stats.getTeam(away_team_id)
        home_team_win = games_frame['HOME_TEAM_WINS'].iloc[index]
        team_stats.recordGame([home_team_id, away_team_id, home_team_win])
        currentGame = Game(home_team, away_team, game_date, rankings_frame, home_team_win)

        if currentGame.hasSufficientData():
            games_list.append(currentGame)

        # just for us so we can see the CSV being processed (its boring to wait)
        if index == nextProgressPrint:
            print(f"{progress * 10}%")
            progress = progress + 1
            nextProgressPrint = tenPercentData * progress

    # print(games_list[0]) this shows how we can print games to examine the feature values
    game_writer = GameWriter(FILE_PATH, games_list)
    game_writer.write()
# ------------------------------------------------------------------------------------
YEAR_FOR_TESTING = 2020
FILE_PATH_TEST = f"data/{YEAR_FOR_TESTING}_games.csv"
FILE_PATH_TRAIN = f"data/{YEAR_TO_GENERATE}_games.csv"
training_csv_dataframe = pd.read_csv(FILE_PATH_TRAIN)
testing_csv_dataframe = pd.read_csv(FILE_PATH_TEST)
num_columns = len(training_csv_dataframe.columns)

x_input_features = training_csv_dataframe.iloc[:, range(0, num_columns - 1)]
y_output_data = training_csv_dataframe.iloc[:, [num_columns - 1]]
model = LogisticRegression(penalty='none', max_iter=200).fit(x_input_features, np.array(y_output_data).ravel())

test_x_input_features = testing_csv_dataframe.iloc[:, range(0, num_columns - 1)]
test_y_output_data = testing_csv_dataframe.iloc[:, [num_columns - 1]]
y_pred = model.predict(test_x_input_features)
print(f'Model Accuracy : {accuracy_score(y_true=test_y_output_data, y_pred=y_pred)}')

# baseline = DummyClassifier(strategy="uniform")
# baseline = DummyClassifier(strategy="most_frequent")
baseline = DummyClassifier(strategy="stratified")
baseline.fit(x_input_features, y_output_data)
print(f"Baseline Accuracy = {accuracy_score(y_pred=baseline.predict(x_input_features), y_true=y_output_data)}")
