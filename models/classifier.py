import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, f1_score, classification_report, ConfusionMatrixDisplay
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt

class Classifier:
    def __init__(self):
        self.df_train = pd.read_csv('../datasets/data/vital_signals_train.txt', sep=',')
        self.x_train = self.df_train.drop(columns=['id', 'gravity', 'label'])
        self.y_train = self.df_train['label']

        self.df_test = pd.read_csv('../datasets/data/vital_signals_test.txt', sep=',')
        self.x_test = self.df_test.drop(columns=['id', 'gravity', 'label'])
        self.y_test = self.df_test['label']
        
        self.model = RandomForestClassifier(random_state=42)

    def train(self):
        parameters = {
            'n_estimators': [115],
            'max_depth': [16],
            'min_samples_split': [2],
            'min_samples_leaf': [1],
        }
        grid = GridSearchCV(self.model, param_grid=parameters, scoring='f1_macro', cv=3, verbose=4)
        grid.fit(self.x_train, self.y_train)
        
        print(grid.best_params_)
    
        self.model = grid.best_estimator_

    def predict(self):
        y_pred = self.model.predict(self.x_test)
        self.plot(y_pred)

    def plot(self, y_pred):
        importances = pd.Series(self.model.feature_importances_, index=self.x_train.columns)
        importances.sort_values(ascending=True).plot(kind='barh', figsize=(8,6))
        print(classification_report(self.y_test, y_pred))
        cm = confusion_matrix(self.y_test, y_pred, labels=self.model.classes_)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=self.model.classes_)
        disp.plot()
        plt.show()

    def export(self):
        joblib.dump(self.model, 'classifier.pkl')

def main():
    model = Classifier()
    model.train()
    model.predict()
    model.export()

if __name__ == "__main__":
    main()