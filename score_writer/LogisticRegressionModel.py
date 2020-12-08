from sklearn.linear_model import LogisticRegression
import pandas as pd
from sklearn.metrics import accuracy_score

#
# results = pd.read_csv()
#
# '''
# train the model
# '''
#
# gameOutcomes = results.iloc[8]


csv_dataframe = pd.read_csv("../data/2019_games.csv")
x_input_features = csv_dataframe.iloc[:, [0,1,2,3,4,5,6, 7]]
y_output_data = csv_dataframe.iloc[:, [8]]  # split into feature vectors and output data
model = LogisticRegression(penalty='none').fit(x_input_features, y_output_data)


y_pred = model.predict(x_input_features)
accuracy = accuracy_score(y_true=y_output_data, y_pred=y_pred)
print(accuracy)