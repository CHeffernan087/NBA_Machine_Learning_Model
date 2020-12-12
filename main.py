import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from helper_functions import cross_validate, HyperParam
from sklearn.svm import SVC
from sklearn.linear_model import RidgeClassifier
from feature_processing.feature_selector import FeatureSelector

from CSVGenerator import CSVGenerator


def parseInput(user_input):
    user_input = user_input.lower()[0]
    if user_input == "y":
        return True
    return False


YEAR_TO_GENERATE = 2018

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
model = LogisticRegression(penalty='none', max_iter=900).fit(x_input_features, np.array(y_output_data).ravel())

# cross_validate(LogisticRegression, HyperParam.C, [0.001, 0.01, 0.1, 1, 10, 50, 80], x_input_features,
#                y_output_data, max_iter=900)
#
# # any more than 2 and it will take a good while. Also need a decent amount of iterations to avoid warning
# cross_validate(LogisticRegression, HyperParam.POWER, [1, 2], x_input_features,
#                y_output_data, max_iter=5000)
#
# cross_validate(SVC, HyperParam.GAMMA, [0.001, 0.01, 0.1, 1, 10, 50, 80], x_input_features,
#                y_output_data, max_iter=900)
#
# cross_validate(SVC, HyperParam.C, [0.001, 0.01, 0.1, 1, 10, 50, 80], x_input_features,
#                y_output_data, max_iter=900)
#
# cross_validate(RidgeClassifier, HyperParam.ALPHA, [0.001, 0.01, 0.1, 1, 10, 50, 80], x_input_features,
#                y_output_data, max_iter=900)


test_x_input_features = testing_csv_dataframe.drop('HOME_TEAM_WINS', axis=1)
test_y_output_data = testing_csv_dataframe['HOME_TEAM_WINS']
y_pred = model.predict(test_x_input_features)
print(f'Model Accuracy : {accuracy_score(y_true=test_y_output_data, y_pred=y_pred)}')

feature_selector = FeatureSelector(testing_csv_dataframe, training_csv_dataframe)

feature_selector.recursive_feature_selection()

# baseline = DummyClassifier(strategy="uniform")
# baseline = DummyClassifier(strategy="most_frequent")
baseline = DummyClassifier(strategy="stratified")
baseline.fit(x_input_features, y_output_data)
print(f"Baseline Accuracy = {accuracy_score(y_pred=baseline.predict(x_input_features), y_true=y_output_data)}")
