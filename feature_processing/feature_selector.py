import pandas as pd
import feature_processing.feature_processor as fp
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import RFECV, SelectKBest
import sklearn.feature_selection as fs


class FeatureSelector:
    def __init__(self, training_data, testing_data):
        self.features = training_data.drop('HOME_TEAM_WINS', axis=1)
        self.labels = training_data['HOME_TEAM_WINS']

        self.test_features = testing_data.drop('HOME_TEAM_WINS', axis=1)
        self.test_labels = testing_data['HOME_TEAM_WINS']

        self.scaling_functions = [fp.min_max_scale_features, fp.standard_scale_features, fp.max_abs_scale_features,
                                  fp.robust_scale_features, fp.power_transform_scale_features,
                                  fp.quantile_scale_features, fp.quantile_2_scale_features, fp.normalise_scale_features]

        self.score_functions = [fs.mutual_info_classif, fs.f_classif, fs.chi2]

    def select_k_best(self):
        k = 6
        best_features = {}
        for fn in self.scaling_functions:
            norm_features = fn(self.features)
            for sf in self.score_functions:
                try:
                    selector = SelectKBest(sf, k=k).fit(norm_features, self.labels)
                    selected_features = self.features.iloc[:, selector.get_support()].columns
                    for feature in selected_features:
                        if feature in best_features:
                            best_features[feature] = best_features[feature] + 1
                        else:
                            best_features[feature] = 1
                except ValueError:
                    continue
        print(best_features)

    def recursive_feature_selection(self):
        accuracy_scores = {}
        for fn in self.scaling_functions:
            norm_features = fn(self.features)
            estimator = LogisticRegression()
            selector = RFECV(estimator, step=1, cv=5).fit(norm_features, self.labels)

            selected_features = pd.DataFrame(norm_features).iloc[:, selector.support_]

            model = LogisticRegression(penalty='none', max_iter=900).fit(selected_features, self.labels)
            test_features = pd.DataFrame(fp.min_max_scale_features(self.test_features)).iloc[:, selector.support_]
            y_pred = model.predict(test_features)
            accuracy = accuracy_score(y_true=self.test_labels, y_pred=y_pred)
            accuracy_scores[fn.__name__] = accuracy
            print(f'Model Accuracy with {fn.__name__}: {accuracy}')

        print(accuracy_scores)

    def test_with_all_scaling_methods(self):
        for fn in self.scaling_functions:
            model = LogisticRegression(penalty='none', max_iter=900).fit(fn(self.features), self.labels)
            y_pred = model.predict(fn(self.test_features))
            print(f'Model Accuracy with {fn.__name__} : {accuracy_score(y_true=self.test_labels, y_pred=y_pred)}')
