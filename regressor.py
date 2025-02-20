import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from sklearn.metrics import classification_report, accuracy_score  
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
from sklearn.neural_network import MLPRegressor

def training(file):
    dataframe = pd.DataFrame(pd.read_csv(file))

    x_train = dataframe[['qpa', 'pulse', 'freq']]
    y_train = dataframe['gravity']

    model = MLPRegressor(hidden_layer_sizes=(200,), max_iter=2000, random_state=42)

    model.fit(x_train, y_train)

    return model


def testing(model, file):
    dataframe = pd.read_csv(file)
    x_test = dataframe[['qpa', 'pulse', 'freq']]
    y_test = dataframe['gravity']

    y_pred = model.predict(x_test)

    mse = mean_squared_error(y_test, y_pred) 
    rmse = np.sqrt(mse)  
    r2 = r2_score(y_test, y_pred)  

    print("Root Mean Squared Error (RMSE):", rmse)
    print("R² Score:", r2)
    
def predict(model, data: pd.DataFrame):
    return [float(val) for val in model.predict(data)]

def save(model, file):
    joblib.dump(model, file)

def load(file):
    return joblib.load(file)
