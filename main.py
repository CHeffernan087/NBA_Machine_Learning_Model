import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

from score_writer.game import Game
from score_writer.game_writer import GameWriter
from Team.TeamStats import TeamStats



FILE_PATH = "data/2019_games.csv"

# ---------- (UN)COMMENT THIS TO MAKE CSV FILE / APPEND TO EXISTING CSV ----------------
rankings_frame = pd.read_csv("data/ranking.csv")
games_frame = pd.read_csv("data/games.csv")
teams = pd.read_csv("data/teams.csv")['TEAM_ID']

games_list = []
team_stats = TeamStats(teams)

# for index, game_date in enumerate(games_frame['GAME_DATE_EST']):
#     year = int(game_date.split("-")[0])
#     if year == 2019:
#         home_team_id = games_frame['HOME_TEAM_ID'].iloc[index];
#         away_team_id = games_frame['VISITOR_TEAM_ID'].iloc[index];
#         home_team = team_stats.getTeam(home_team_id)
#         away_team = team_stats.getTeam(away_team_id)
#         home_team_win = games_frame['HOME_TEAM_WINS'].iloc[index]
#         team_stats.recordGame([home_team_id, away_team_id, home_team_win])
#         currentGame = Game(home_team, away_team, game_date, rankings_frame,home_team_win)
#
#         if (currentGame.hasSufficientData()):
#             games_list.append(currentGame)
#
# # print(games_list[0]) this shows how we can print games to examine the feature values
# game_writer = GameWriter(FILE_PATH, games_list)
# game_writer.write()
# ------------------------------------------------------------------------------------

csv_dataframe = pd.read_csv(FILE_PATH)
num_columns = len(csv_dataframe.columns)

x_input_features = csv_dataframe.iloc[:, range(0, num_columns-1)]
y_output_data = csv_dataframe.iloc[:, [num_columns-1]]
model = LogisticRegression(penalty='none',max_iter=200).fit(x_input_features, np.array(y_output_data).ravel())

y_pred = model.predict(x_input_features)
print(f'Model Accuracy : {accuracy_score(y_true=y_output_data, y_pred=y_pred)}')

# baseline = DummyClassifier(strategy="uniform")
# baseline = DummyClassifier(strategy="most_frequent")
baseline = DummyClassifier(strategy="stratified")
baseline.fit(x_input_features, y_output_data)
print(f"Baseline Accuracy = {accuracy_score(y_pred=baseline.predict(x_input_features), y_true=y_output_data)}")
