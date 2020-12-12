import numpy as np
import pandas as pd
from CSVGenerator import CSVGenerator
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def parseInput(user_input):
    user_input = user_input.lower()[0]
    if user_input == "y":
        return True
    return False


YEAR_TO_GENERATE = 2019

userInput = input("Do you want to generate CSV? (y/n)\n> ")
shouldGenCsv = parseInput(userInput)

if shouldGenCsv:
    CSVGenerator(YEAR_TO_GENERATE).generate()

YEAR_FOR_TESTING = 2019
FILE_PATH_TEST = f"data/{YEAR_FOR_TESTING}_games.csv"
FILE_PATH_TRAIN = f"data/{YEAR_TO_GENERATE}_games.csv"

training_csv_dataframe = pd.read_csv(FILE_PATH_TRAIN)
testing_csv_dataframe = pd.read_csv(FILE_PATH_TEST)
num_columns = len(training_csv_dataframe.columns)

x_input_features = training_csv_dataframe.drop('HOME_TEAM_WINS', axis=1)
y_output_data = training_csv_dataframe['HOME_TEAM_WINS']
model = LogisticRegression(penalty='none', max_iter=500).fit(x_input_features, np.array(y_output_data).ravel())

test_x_input_features = testing_csv_dataframe.drop('HOME_TEAM_WINS', axis=1)
test_y_output_data = testing_csv_dataframe['HOME_TEAM_WINS']
y_pred = model.predict(test_x_input_features)
print(f'Model Accuracy : {accuracy_score(y_true=test_y_output_data, y_pred=y_pred)}')

# baseline = DummyClassifier(strategy="uniform")
# baseline = DummyClassifier(strategy="most_frequent")
baseline = DummyClassifier(strategy="stratified")
baseline.fit(x_input_features, y_output_data)
print(f"Baseline Accuracy = {accuracy_score(y_pred=baseline.predict(x_input_features), y_true=y_output_data)}")
