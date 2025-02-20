import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from sklearn.ensemble import GradientBoostingRegressor

def training(file):
    dataframe = pd.DataFrame(pd.read_csv(file))

    x_train = dataframe[['qpa', 'pulse', 'freq']]
    y_train = dataframe['gravity']

    model = DecisionTreeRegressor(random_state=32, max_depth=50, min_samples_leaf=50)

    parameters = {
        'max_depth': [50],
        'min_samples_leaf': [10]
    }   

    clf = GridSearchCV(model, parameters, cv=5, scoring='f1_weighted', verbose=4)
    clf.fit(x_train, y_train)

    best = clf.best_estimator_

    return best

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
    return model.predict(data[['qpa', 'pulse', 'freq']].values)

def save(model, file):
    joblib.dump(model, file)

def load(file):
    return joblib.load(file)
