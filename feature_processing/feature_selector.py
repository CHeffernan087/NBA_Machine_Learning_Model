import feature_processing.feature_processor as fp
from sklearn.metrics import accuracy_score

from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import RFECV


class FeatureSelector:
    def __init__(self, training_data, testing_data):
        self.features = training_data.drop('HOME_TEAM_WINS', axis=1)
        self.labels = training_data['HOME_TEAM_WINS']

        self.test_features = testing_data.drop('HOME_TEAM_WINS', axis=1)
        self.test_labels = testing_data['HOME_TEAM_WINS']

    def recursive_feature_selection(self):
        norm_features = fp.min_max_scale_features(self.features)
        estimator = LogisticRegression()
        selector = RFECV(estimator, step=1, cv=5).fit(norm_features, self.labels)

        print(self.features.iloc[:, selector.support_].columns)

    def test_with_all_scaling_methods(self):
        scaling_functions = [fp.min_max_scale_features, fp.standard_scale_features, fp.max_abs_scale_features,
                             fp.robust_scale_features, fp.power_transform_scale_features, fp.quantile_scale_features,
                             fp.quantile_2_scale_features, fp.normalise_scale_features]

        for fn in scaling_functions:
            model = LogisticRegression(penalty='none', max_iter=500).fit(fn(self.features), self.labels)
            y_pred = model.predict(fn(self.test_features))
            print(f'Model Accuracy with {fn.__name__} : {accuracy_score(y_true=self.test_labels, y_pred=y_pred)}')
