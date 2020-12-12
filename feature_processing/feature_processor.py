from sklearn.preprocessing import MinMaxScaler


def min_max_scale_features(features):
    return MinMaxScaler().fit(features).transform(features)
