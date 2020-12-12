from feature_processor import min_max_scale_features

from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import RFECV


class FeatureSelector:
    def __init__(self, training_data):
        self.features = training_data.drop('HOME_TEAM_WINS', axis=1)
        self.labels = training_data['HOME_TEAM_WINS']

    def recursive_feature_selection(self):
        norm_features = min_max_scale_features(self.features)
        estimator = LogisticRegression()
        selector = RFECV(estimator, step=1, cv=5).fit(norm_features, self.labels)

        print(self.features.iloc[:, selector.support_].columns)
