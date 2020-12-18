from enum import Enum
from typing import Union, Type

import numpy
import numpy as np
from matplotlib import pyplot
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import RidgeClassifier
from sklearn.metrics import mean_squared_error, log_loss
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier


class HyperParam(Enum):
    C = 1
    POWER = 2
    GAMMA = 3
    K = 4


def cross_validate(model_type: Union[Type[LogisticRegression], Type[KNeighborsClassifier], Type[SVC]],
                   hyper_param: HyperParam, hyper_param_values_list, x_training_data, y_training_data, k_fold_splits=10,
                   penalty_type="l2", max_iter=None, weights=None):
    print("cross validating....")
    x_training_data = np.array(x_training_data)
    y_training_data = np.array(y_training_data)
    log_loss_list = []
    standard_dev = []

    for param in hyper_param_values_list:
        print(f"validating for {hyper_param} {param}")

        model_params = {}
        if hyper_param == HyperParam.C:
            model_params['C'] = param
        if max_iter is not None:
            model_params['max_iter'] = max_iter
        if weights is not None:
            model_params["weights"] = weights
        if model_type == LogisticRegression:
            model_params['penalty'] = penalty_type
        elif model_type == SVC and hyper_param == HyperParam.GAMMA:
            model_params['gamma'] = param
        elif model_type == KNeighborsClassifier:
            model_params["n_neighbors"] = param

        model = model_type(**model_params)
        pipeline = make_pipeline(StandardScaler(), model)

        if hyper_param == HyperParam.POWER:
            x_training_data = PolynomialFeatures(param).fit_transform(x_training_data)

        temp = []
        kf = KFold(n_splits=k_fold_splits)
        for train, test in kf.split(x_training_data):
            pipeline.fit(x_training_data[train], y_training_data[train].ravel())
            y_pred = pipeline.predict(x_training_data[test])
            temp.append(log_loss(y_training_data[test], y_pred))
        log_loss_list.append(numpy.array(temp).mean())
        standard_dev.append(numpy.array(temp).std())

    pyplot.errorbar(hyper_param_values_list, log_loss_list, yerr=standard_dev, label="Standard Deviation")
    pyplot.title(f"Prediction error vs {hyper_param} - {model_type.__name__}")
    pyplot.xlabel(f"{hyper_param} Value")
    pyplot.ylabel("Log loss")
    pyplot.legend()
    pyplot.show()
