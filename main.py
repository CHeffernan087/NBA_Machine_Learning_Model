import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from helper_functions import cross_validate, HyperParam
from sklearn.svm import SVC
from sklearn.linear_model import RidgeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_classification
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from feature_processing.feature_selector import FeatureSelector

from CSVGenerator import CSVGenerator


def parseInput(user_input):
    user_input = user_input.lower()[0]
    if user_input == "y":
        return True
    return False


YEARS_FOR_TRAINING = [2015,2016,2017,2018]
YEAR_FOR_TESTING = 2019

test_file_name = f"training_data_{YEARS_FOR_TRAINING[0]}-{YEARS_FOR_TRAINING[-1]}.csv"
should_scrape_data = parseInput(input("Do you want to scrape the data? (y/n)\n> "))
should_gen_csv = parseInput(input("Do you want to generate CSV? (y/n)\n> "))

if should_scrape_data:
    CSVGenerator(0).scrapeAllTrainingData(YEARS_FOR_TRAINING)
    CSVGenerator(YEAR_FOR_TESTING).generate_game_stats()

if should_gen_csv:
    CSVGenerator(0).generate_multiple_years(YEARS_FOR_TRAINING)
    CSVGenerator(YEAR_FOR_TESTING).generate()


FILE_PATH_TEST = f"data/{YEAR_FOR_TESTING}_games.csv"
FILE_PATH_TRAIN = f"data/training_features/training_features_{YEARS_FOR_TRAINING[0]}-{YEARS_FOR_TRAINING[-1]}.csv"

training_csv_dataframe = pd.read_csv(FILE_PATH_TRAIN)
testing_csv_dataframe = pd.read_csv(FILE_PATH_TEST)
num_columns = len(training_csv_dataframe.columns)

x_input_features = training_csv_dataframe.iloc[:, range(0, num_columns - 1)]
y_output_data = training_csv_dataframe.iloc[:, [num_columns - 1]]

model = LogisticRegression(penalty='none', max_iter=900).fit(x_input_features, np.array(y_output_data).ravel())

# from sklearn.preprocessing import StandardScaler
# from sklearn.pipeline import make_pipeline
# model = make_pipeline(StandardScaler(), LogisticRegression(class_weight='auto',penalty='none', max_iter=900))
# model.fit(x_input_features, np.array(y_output_data).ravel())

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


test_x_input_features = testing_csv_dataframe.iloc[:, range(0, num_columns - 1)]
test_y_output_data = testing_csv_dataframe.iloc[:, [num_columns - 1]]
y_pred = model.predict(test_x_input_features)
print(f'Model Accuracy : {accuracy_score(y_true=test_y_output_data, y_pred=y_pred)}')

hidden_layer_size = (int(len(x_input_features.columns) / 2), )
nn_model = MLPClassifier(random_state=4, hidden_layer_sizes=hidden_layer_size)
nn_model = nn_model.fit(x_input_features, np.array(y_output_data).ravel())
y_pred = nn_model.predict(test_x_input_features)
print(f'Neural Network Model Accuracy : {accuracy_score(y_true=test_y_output_data, y_pred=y_pred)}')

feature_selector = FeatureSelector(training_csv_dataframe, testing_csv_dataframe)

rfe_train_x, rfe_test_x = feature_selector.get_rfe_train_test_split()
model = LogisticRegression(penalty='none', max_iter=900).fit(rfe_train_x, np.array(y_output_data).ravel())
y_pred = model.predict(rfe_test_x)
print(f'Model Accuracy with RFECV best features: {accuracy_score(y_true=test_y_output_data, y_pred=y_pred)}')

k_best_train_x, k_best_test_x = feature_selector.get_k_best_train_test_split()
model = LogisticRegression(penalty='none', max_iter=900).fit(k_best_train_x, np.array(y_output_data).ravel())
y_pred = model.predict(k_best_test_x)
print(f'Model Accuracy with k best features: {accuracy_score(y_true=test_y_output_data, y_pred=y_pred)}')

# baseline = DummyClassifier(strategy="uniform")
# baseline = DummyClassifier(strategy="most_frequent")
baseline = DummyClassifier(strategy="stratified")
baseline.fit(x_input_features, y_output_data)
print(f"Baseline Accuracy = {accuracy_score(y_pred=baseline.predict(x_input_features), y_true=y_output_data)}")
