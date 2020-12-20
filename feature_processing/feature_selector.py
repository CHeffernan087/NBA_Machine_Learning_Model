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

        self.test_features = testing_data.iloc[:, :-1]
        self.test_labels = testing_data.iloc[:, -1]

        self.scaling_functions = [fp.min_max_scale_features, fp.standard_scale_features, fp.max_abs_scale_features,
                                  fp.robust_scale_features, fp.power_transform_scale_features,
                                  fp.quantile_scale_features, fp.quantile_2_scale_features, fp.normalise_scale_features]

    def select_k_best(self, k=10, score_func=fs.mutual_info_classif, verbose=False):
        selector = SelectKBest(score_func=score_func, k=k).fit(self.features, self.labels)
        selected_features = self.features.iloc[:, selector.get_support()].columns

        if verbose:
            print(f"Selected {k} best features with {score_func.__name__}:")
            print(selected_features)

        return selected_features

    def recursive_feature_selection(self, estimator=LogisticRegression(max_iter=900), verbose=False):
        selector = RFECV(estimator, step=1, cv=5).fit(self.features, self.labels)

        selected_features = pd.DataFrame(self.features).iloc[:, selector.support_]

        model = LogisticRegression(penalty='none', max_iter=900).fit(selected_features, self.labels)
        test_features = pd.DataFrame(self.test_features).iloc[:, selector.support_]

        y_pred = model.predict(test_features)
        accuracy = accuracy_score(y_true=self.test_labels, y_pred=y_pred)

        if verbose:
            print(f'Model Accuracy with RFECV: {accuracy}')
            print(f"Selected Columns = {selected_features.columns}")

        return selected_features.columns

    def test_with_all_scaling_methods(self):
        for fn in self.scaling_functions:
            model = LogisticRegression(penalty='none', max_iter=900).fit(fn(self.features), self.labels)
            y_pred = model.predict(fn(self.test_features))
            print(f'Model Accuracy with {fn.__name__} : {accuracy_score(y_true=self.test_labels, y_pred=y_pred)}')

    def get_k_best_train_test_split(self):
        feature_cols = self.select_k_best(k=10)
        train_x = self.features[feature_cols]
        col_indices = [self.features.columns.get_loc(c) for c in feature_cols if c in self.features]
        test_x = self.test_features.iloc[:, col_indices]

        return train_x, test_x

    def get_rfe_train_test_split(self):
        feature_cols = self.recursive_feature_selection()
        train_x = self.features[feature_cols]
        col_indices = [self.features.columns.get_loc(c) for c in feature_cols if c in self.features]
        test_x = self.test_features.iloc[:, col_indices]

        return train_x, test_x
