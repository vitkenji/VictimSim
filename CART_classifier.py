import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score

def training(file):
    dataframe = pd.DataFrame(pd.read_csv(file))
    X = dataframe[['qpa', 'pulse', 'freq']]
    y = dataframe['output']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = DecisionTreeClassifier(random_state=42)

    parameters = {
        'criterion': ['entropy', 'gini'],
        'max_depth': [8],
        'min_samples_leaf': [8]
    }   

    clf = GridSearchCV(model, parameters, cv=5, scoring='f1_weighted', verbose=4)
    clf.fit(X_train, y_train)

    best = clf.best_estimator_

    train_acc = accuracy_score(y_train, best.predict(X_train))
    test_acc = accuracy_score(y_test, best.predict(X_test))

    print("\n* Parametros do classificador *")
    print(best.get_params())

    print(f"Acurácia no treino: {train_acc:.4f}")

    return best

def testing(model, file):
    dataframe = pd.DataFrame(pd.read_csv(file))
    x_test = dataframe[['qpa', 'pulse', 'freq']]
    y_test = dataframe['output']
    y_pred = model.predict(x_test)
    print(f"Acurácia do teste: {accuracy_score(y_test, y_pred)}")
    print("Relatório de Classificação:")
    print(classification_report(y_test, y_pred))

def predict(model, data: pd.DataFrame):
    prediction_classes = model.predict(data)
    return prediction_classes

def save(model, file):
    joblib.dump(model, file)

def load(file):
    return joblib.load(file)
