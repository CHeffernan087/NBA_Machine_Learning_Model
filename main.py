import numpy as np
import pandas as pd
from matplotlib import pyplot
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from CSVGenerator import CSVGenerator


def parseInput(user_input):
    user_input = user_input.lower()[0]
    if user_input == "y":
        return True
    return False


YEARS_FOR_TRAINING = [2015, 2016, 2017, 2018]
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

test_x_input_features = testing_csv_dataframe.iloc[:, range(0, num_columns - 1)]
test_y_output_data = testing_csv_dataframe.iloc[:, [num_columns - 1]]

log_loss_list = []
standard_dev = []
x_training_data = np.array(x_input_features)
y_training_data = np.array(y_output_data)
for c_value in [0.001, 0.01, 0.1, 1, 5, 10, 15, 20]:
    logistic_model = LogisticRegression(class_weight='auto', max_iter=900, C=c_value)

    pipeline = make_pipeline(StandardScaler(), logistic_model)
    pipeline.fit(x_training_data, np.array(y_training_data).ravel())

    temp = []
    kf = KFold(n_splits=10)
    for train, test in kf.split(x_training_data):
        pipeline.fit(x_training_data[train], y_training_data[train].ravel())
        y_pred = pipeline.predict(x_training_data[test])
        temp.append(log_loss(y_training_data[test], y_pred))
    log_loss_list.append(np.array(temp).mean())
    standard_dev.append(np.array(temp).std())

# num_features_to_accuracy_dit = {}
# for n in range(len(x_input_features.columns)):
#     selector = RFE(logistic_model, n_features_to_select=n + 1)
#
#     pipeline = make_pipeline(StandardScaler(), selector, logistic_model)
#     pipeline.fit(x_input_features, np.array(y_output_data).ravel())
#
#     y_pred = pipeline.predict(test_x_input_features)
#     num_features_to_accuracy_dit[n] = accuracy_score(y_true=test_y_output_data, y_pred=y_pred)
#
# ideal_num_features = 0
# current_accuracy = 0
# for key, value in num_features_to_accuracy_dit.items():
#     if value >= current_accuracy:
#         ideal_num_features = key

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

# print(f"Ideal num features = {ideal_num_features}")

pyplot.errorbar([0.001, 0.01, 0.1, 1, 5, 10, 15, 20], log_loss_list, yerr=standard_dev, label="Standard Deviation")
pyplot.title(f"Prediction error vs C - logistic")
pyplot.xlabel(f"C Value")
pyplot.ylabel("log loss")
pyplot.legend()
pyplot.show()

logistic_model = LogisticRegression(class_weight='auto', max_iter=900, C=1)  # from above plot

pipeline = make_pipeline(StandardScaler(), logistic_model)
pipeline.fit(x_training_data, np.array(y_training_data).ravel())

y_pred = pipeline.predict(test_x_input_features)
print(f'Model Accuracy : {accuracy_score(y_true=test_y_output_data, y_pred=y_pred)}')

# baseline = DummyClassifier(strategy="uniform")
# baseline = DummyClassifier(strategy="most_frequent")
baseline = DummyClassifier(strategy="stratified")
baseline.fit(x_input_features, y_output_data)
print(f"Baseline Accuracy = {accuracy_score(y_pred=baseline.predict(x_input_features), y_true=y_output_data)}")
