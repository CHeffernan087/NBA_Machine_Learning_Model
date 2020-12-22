import numpy as np
import pandas as pd
from matplotlib import pyplot
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, plot_confusion_matrix, roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from helper_functions import cross_validate, HyperParam
from CSVGenerator import CSVGenerator
from feature_processing.feature_selector import FeatureSelector



def parseInput(user_input):
    user_input = user_input.lower()[0]
    if user_input == "y":
        return True
    return False


years_for_testing = [2015,2016, 2017, 2018, 2019]

should_scrape_data = parseInput(input("Do you want to scrape the data? (y/n)\n> "))
should_gen_csv = parseInput(input("Do you want to generate CSV? (y/n)\n> "))
model_accuracies = {"LOGISTIC":[], "SVC": [], "KNN":[]}


for index,year_for_testing in enumerate(years_for_testing):
    print(f"\n-------  {index+1}/{len(years_for_testing)}: testing on {year_for_testing}  --------\n")

    training_years = [2015,2016, 2017, 2018, 2019]
    training_years.remove(year_for_testing)

    first_iteration_of_k_fold = index == 0
    if should_scrape_data and first_iteration_of_k_fold:
        CSVGenerator(0).scrapeAllTrainingData(training_years)
        CSVGenerator(year_for_testing).generate_game_stats()

    if should_gen_csv:
        CSVGenerator(0).generate_multiple_years(training_years)
        CSVGenerator(year_for_testing).generate()

    FILE_PATH_TEST = f"data/{year_for_testing}_games.csv"
    FILE_PATH_TRAIN = f"data/training_features/training_features_{str(training_years)[1:-1]}.csv"

    training_csv_dataframe = pd.read_csv(FILE_PATH_TRAIN)
    testing_csv_dataframe = pd.read_csv(FILE_PATH_TEST)
    num_columns = len(training_csv_dataframe.columns)

    x_input_features = training_csv_dataframe.iloc[:, range(0, num_columns - 1)]
    y_output_data = training_csv_dataframe.iloc[:, [num_columns - 1]]

    test_x_input_features = testing_csv_dataframe.iloc[:, range(0, num_columns - 1)]
    test_y_output_data = testing_csv_dataframe.iloc[:, [num_columns - 1]]

    if(year_for_testing == 2018):
        num_features_to_accuracy_dit = {}
        # for n in range(len(x_input_features.columns)):
        #     selector = RFE(logistic_model, n_features_to_select=n + 1)
        #     pipeline = make_pipeline(StandardScaler(), selector, logistic_model)
        #     pipeline.fit(x_input_features, np.array(y_output_data).ravel())
        #     y_pred = pipeline.predict(test_x_input_features)
        #     num_features_to_accuracy_dit[n] = accuracy_score(y_true=test_y_output_data, y_pred=y_pred)
        #
        # ideal_num_features = 0
        # current_accuracy = 0
        # for key, value in num_features_to_accuracy_dit.items():
        #     if value >= current_accuracy:
        #         ideal_num_features = key
        # print(f"Ideal num features = {ideal_num_features}")

        # cross_validate(LogisticRegression, HyperParam.C, [0.001, 0.01, 0.1, 1, 5, 10, 15, 20], x_input_features, y_output_data)
        # cross_validate(SVC, HyperParam.GAMMA, [0.000001, 0.00001, 0.0001, 0.001, 0.005, 0.007], x_input_features, y_output_data)
        # cross_validate(SVC, HyperParam.C, [0.001, 0.01, 0.1, 1, 5, 10, 15, 20], x_input_features, y_output_data)
        # cross_validate(KNeighborsClassifier, HyperParam.K, [1, 5, 10, 15, 25, 50, 75, 100, 125, 150, 175, 200],
        #                x_input_features, y_output_data)
        # cross_validate(KNeighborsClassifier, HyperParam.K, [1, 5, 10, 15, 25, 50, 75, 100, 125, 150, 175, 200],
        #                x_input_features, y_output_data, weights="distance")
        # cross_validate(LogisticRegression, HyperParam.POWER, [1, 2], x_input_features, y_output_data, max_iter=1500)


    logistic_model = LogisticRegression(class_weight='auto', max_iter=900, C=1)  # best from above plots
    svc_model = SVC(gamma=0.001, C=1)
    knn_model = KNeighborsClassifier(n_neighbors=100)

    logistic_pipeline = make_pipeline(StandardScaler(), logistic_model)
    logistic_pipeline.fit(x_input_features, np.array(y_output_data).ravel())
    y_pred = logistic_pipeline.predict(test_x_input_features)
    logistic_accuracy = accuracy_score(y_true=test_y_output_data, y_pred=y_pred)
    model_accuracies["LOGISTIC"].append(logistic_accuracy)
    print(f'Logistic Accuracy : {logistic_accuracy}')

    svc_pipeline = make_pipeline(StandardScaler(), svc_model)
    svc_pipeline.fit(x_input_features, np.array(y_output_data).ravel())
    y_pred = svc_pipeline.predict(test_x_input_features)
    svc_accuracy = accuracy_score(y_true=test_y_output_data, y_pred=y_pred)
    model_accuracies["SVC"].append(svc_accuracy)
    print(f'SVC Accuracy : {svc_accuracy}')

    knn_pipeline = make_pipeline(StandardScaler(), knn_model)
    knn_pipeline.fit(x_input_features, np.array(y_output_data).ravel())
    y_pred = knn_pipeline.predict(test_x_input_features)
    knn_accuracy = accuracy_score(y_true=test_y_output_data, y_pred=y_pred)
    model_accuracies["KNN"].append(knn_accuracy)
    print(f'kNN Accuracy : {knn_accuracy}')


    feature_selector = FeatureSelector(training_csv_dataframe, testing_csv_dataframe)
    rfe_input_features, rfe_test_x_input_features = feature_selector.get_rfe_train_test_split()
    logistic_pipeline.fit(rfe_input_features, np.array(y_output_data).ravel())
    y_pred = logistic_pipeline.predict(rfe_test_x_input_features)
    print(f'Logistic Accuracy with RFE selected features: {accuracy_score(y_true=test_y_output_data, y_pred=y_pred)}')

    k_best_input_features, k_best_test_x_input_features = feature_selector.get_k_best_train_test_split()
    logistic_pipeline.fit(k_best_input_features, np.array(y_output_data).ravel())
    y_pred = logistic_pipeline.predict(k_best_test_x_input_features)
    print(f'Logistic Accuracy with K best selected features: {accuracy_score(y_true=test_y_output_data, y_pred=y_pred)}')

    pyplot.title('ROC Curves')
    pyplot.ylabel('True Positive Rate')
    pyplot.xlabel('False Positive Rate')

    if(year_for_testing == 2019):
        # split into x and y testing & training data
        x_train, x_test, y_train, y_test = train_test_split(x_input_features, y_output_data, test_size=0.2)
        knn_pipeline.fit(x_train, np.array(y_train).ravel())
        fpr, tpr, _ = roc_curve(y_test, knn_pipeline.predict_proba(x_test)[:, 1])
        roc_auc = auc(fpr, tpr)  # get the area under the curve
        pyplot.plot(fpr, tpr, color="blue", label='KNN AUC = %0.8f' % roc_auc)  # plot the curve

        svc_pipeline.fit(x_train, np.array(y_train).ravel())
        fpr, tpr, _ = roc_curve(y_test, svc_pipeline.decision_function(x_test))
        roc_auc = auc(fpr, tpr)
        pyplot.plot(fpr, tpr, color="green", label='SVC AUC = %0.8f' % roc_auc)

        logistic_pipeline.fit(x_train, np.array(y_train).ravel())
        fpr, tpr, _ = roc_curve(y_test, logistic_pipeline.decision_function(x_test))
        roc_auc = auc(fpr, tpr)
        pyplot.plot(fpr, tpr, color="orange", label='Logistic Regression AUC = %0.8f' % roc_auc)

        baseline_pipeline = make_pipeline(StandardScaler(), DummyClassifier(strategy="most_frequent"))
        baseline_pipeline.fit(x_train, np.array(y_train).ravel())
        fpr, tpr, _ = roc_curve(y_test, baseline_pipeline.predict_proba(x_test)[:, 1])
        roc_auc = auc(fpr, tpr)
        pyplot.plot(fpr, tpr, color="red", label='Baseline AUC = %0.8f' % roc_auc)

        pyplot.legend(loc='lower right')
        pyplot.show()

        best_pipeline = logistic_pipeline
        plot_confusion_matrix(best_pipeline, test_x_input_features, test_y_output_data)
        pyplot.title("Logistic Regression")
        pyplot.show()

        baseline_pipeline.fit(x_input_features, y_output_data)
        plot_confusion_matrix(baseline_pipeline, test_x_input_features, test_y_output_data)
        pyplot.title("Most Frequent Baseline")
        pyplot.show()

        print(f"Baseline Accuracy: {accuracy_score(y_pred=baseline_pipeline.predict(test_x_input_features), y_true=test_y_output_data)}")
        print(f"\n-------  end of testing on {year_for_testing}  --------\n")

print("------ AVERAGE ACCURACY -------")
print("\nLogistic Regression:")
print(f"K-Fold Results : {np.array(model_accuracies['LOGISTIC'])}")
print(f"Mean Accuracy : {np.mean(model_accuracies['LOGISTIC'])}")
print(f"Variance:{np.var(model_accuracies['LOGISTIC'])}")
print("\nSVC:")
print(f"K-Fold Results : {np.array(model_accuracies['SVC'])}")
print(f"Mean Accuracy : {np.mean(model_accuracies['SVC'])}")
print(f"Variance:{np.var(model_accuracies['SVC'])}")
print("\nKNN:")
print(f"K-Fold Results : {np.array(model_accuracies['KNN'])}")
print(f"Mean Accuracy : {np.mean(model_accuracies['KNN'])}")
print(f"Variance:{np.var(model_accuracies['KNN'])}")
