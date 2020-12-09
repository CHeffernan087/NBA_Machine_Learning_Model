import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from score_writer.game import Game
from score_writer.game_writer import GameWriter

FILE_PATH = "data/2019_games.csv"

# ---------- (UN)COMMENT THIS TO MAKE CSV FILE / APPEND TO EXISTING CSV ----------------
rankings_frame = pd.read_csv("data/ranking.csv")
games_frame = pd.read_csv("data/games.csv")

games_list = []

for index, game_date in enumerate(games_frame['GAME_DATE_EST']):
    year = int(game_date.split("-")[0])
    if year == 2019:
        home_team = games_frame['HOME_TEAM_ID'].iloc[index]
        away_team = games_frame['VISITOR_TEAM_ID'].iloc[index]
        home_team_win = games_frame['HOME_TEAM_WINS'].iloc[index]
        games_list.append(Game(home_team, away_team, game_date, rankings_frame, home_team_win))

# print(games_list[0]) this shows how we can print games to examine the feature values
game_writer = GameWriter(FILE_PATH, games_list)
game_writer.write()
# ------------------------------------------------------------------------------------

csv_dataframe = pd.read_csv(FILE_PATH)
x_input_features = csv_dataframe.iloc[:, range(0, 8)]
y_output_data = csv_dataframe.iloc[:, [8]]
model = LogisticRegression().fit(x_input_features, np.array(y_output_data).ravel())

y_pred = model.predict(x_input_features)
print(f'Model Accuracy : {accuracy_score(y_true=y_output_data, y_pred=y_pred)}')

# baseline = DummyClassifier(strategy="uniform")
# baseline = DummyClassifier(strategy="most_frequent")
baseline = DummyClassifier(strategy="stratified")
baseline.fit(x_input_features, y_output_data)
print(f"Baseline Accuracy = {accuracy_score(y_pred=baseline.predict(x_input_features), y_true=y_output_data)}")
