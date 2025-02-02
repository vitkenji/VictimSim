import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

def training(file):
    print("regressor training")
    dataframe = pd.DataFrame(pd.read_csv(file))

    x_train = dataframe[['qpa', 'pulse', 'freq']]
    y_train = dataframe['gravity']

    model = GradientBoostingRegressor(loss='absolute_error', max_depth=100, random_state=32)

    model.fit(x_train, y_train)

    return model

def testing(model, file):
    dataframe = pd.DataFrame(pd.read_csv(file))
    predicting = model.predict(dataframe[['qpa', 'pulse', 'freq']])

def predict(model, data: pd.DataFrame):
    return [float(val) for val in model.predict(data)]

def save(model, file):
    joblib.dump(model, file)

def load(file):
    return joblib.load(file)
