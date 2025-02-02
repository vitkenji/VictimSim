import joblib
import pandas as pd
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Softmax
from tensorflow.keras.utils import to_categorical

def training(file):
    dataframe = pd.DataFrame(pd.read_csv(file))
    x_train = dataframe[['qpa','pulse','freq']]
    y_train = dataframe['output']
    y_train = y_train - 1  

    model = Sequential()
    model.add(Dense(128, input_dim=x_train.shape[1], activation='relu'))
    model.add(Dense(64, activation='relu')) 
    model.add(Dense(4, activation='softmax')) 

    model.compile(optimizer=Adam(learning_rate=0.01), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    model.fit(x_train, y_train, epochs=100, batch_size=32, verbose=1)

    return model

def testing(model, file):
    dataframe = pd.DataFrame(pd.read_csv(file))
    return model.predict(dataframe[['qpa','pulse', 'freq']]).argmax(axis=1)

def predict(model, data: pd.DataFrame):
    prediction_classes = model.predict(data).argmax(axis=1) 
    return prediction_classes + 1 

def save(model, file):
    joblib.dump(model, file)

def load(file):
    return joblib.load(file)
