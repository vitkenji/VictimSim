import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt

class Regressor:
    def __init__(self):
        self.df_train = pd.read_csv('../datasets/data/vital_signals_train.txt', sep=',')
        self.x_train = self.df_train.drop(columns=['id', 'gravity', 'label'])
        self.y_train = self.df_train['gravity']

        self.df_test = pd.read_csv('../datasets/data/vital_signals_test.txt', sep=',')
        self.x_test = self.df_test.drop(columns=['id', 'gravity', 'label'])
        self.y_test = self.df_test['gravity']
        
        self.model = GradientBoostingRegressor(random_state=42)

    def train(self):
        parameters = {
            'learning_rate': [0.24, 0.25, 0.26],
            'subsample': [1],
        }
        grid = GridSearchCV(self.model, param_grid=parameters, scoring='r2', cv=3, verbose=4)
        grid.fit(self.x_train, self.y_train)
        
        print(grid.best_params_)
    
        self.model = grid.best_estimator_

    def predict(self):
        y_pred = self.model.predict(self.x_test)
        self.plot(y_pred)

    def plot(self, y_pred):
        plt.scatter(self.y_test, y_pred, alpha=0.5)
        plt.plot([self.y_test.min(), self.y_test.max()],[self.y_test.min(), self.y_test.max()], 'r--')
        print(f"MSE: {mean_squared_error(self.y_test, y_pred)}")
        print(f"R2: {r2_score(self.y_test, y_pred)}")
        plt.show()

    def export(self):
        joblib.dump(self.model, 'regressor.pkl')

def main():
    model = Regressor()
    model.train()
    model.predict()
    model.export()

if __name__ == "__main__":
    main()