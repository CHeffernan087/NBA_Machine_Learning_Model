from enum import Enum
from typing import Union, Type

import numpy
import numpy as np
from matplotlib import pyplot
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import RidgeClassifier
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVC


class HyperParam(Enum):
    C = 1
    POWER = 2
    GAMMA = 3
    ALPHA = 4


def cross_validate(model_type: Union[Type[LogisticRegression], Type[RidgeClassifier], Type[SVC]],
                   hyper_param: HyperParam, hyper_param_values_list, x_training_data, y_training_data, k_fold_splits=10,
                   penalty_type="l2", max_iter=None):
    print("cross validating....")
    x_training_data = np.array(x_training_data)
    y_training_data = np.array(y_training_data)
    mean_error = []
    standard_dev = []

    for param in hyper_param_values_list:
        print(f"validating for {hyper_param} {param}")

        model_params = {}
        if hyper_param == HyperParam.C:
            model_params['C'] = param
        if max_iter is not None:
            model_params['max_iter'] = max_iter
        if model_type == LogisticRegression:
            model_params['penalty'] = penalty_type
        elif model_type == SVC and hyper_param == HyperParam.GAMMA:
            model_params['gamma'] = param
        elif model_type == RidgeClassifier and hyper_param == HyperParam.ALPHA:
            model_params['alpha'] = param

        model = model_type(**model_params)

        if hyper_param == HyperParam.POWER:
            x_training_data = PolynomialFeatures(param).fit_transform(x_training_data)

        temp = []
        kf = KFold(n_splits=k_fold_splits)
        for train, test in kf.split(x_training_data):
            model.fit(x_training_data[train], y_training_data[train].ravel())
            y_pred = model.predict(x_training_data[test])
            temp.append(mean_squared_error(y_training_data[test], y_pred))
        mean_error.append(numpy.array(temp).mean())
        standard_dev.append(numpy.array(temp).std())

    pyplot.errorbar(hyper_param_values_list, mean_error, yerr=standard_dev, label="Standard Deviation")
    pyplot.title(f"Prediction error vs {hyper_param} - {model_type.__name__}")
    pyplot.xlabel(f"{hyper_param} Value")
    pyplot.ylabel("Mean square error")
    pyplot.legend()
    pyplot.show()
