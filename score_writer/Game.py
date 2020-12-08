import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from operator import itemgetter
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error
from sklearn import linear_model
from sklearn.model_selection import KFold
import matplotlib.patches as mpatches

class Game():
    def __init__(self):
        pass


file = pd.read_csv("../data/ranking.csv", header=None, low_memory=False)
x1_points = file[0]
x2_points = file[1]
outcomes = file[2]

print(x1_points)