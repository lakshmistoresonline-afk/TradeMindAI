import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

class StockLSTM:
    def __init__(self, sequence_length=60):
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def prepare_data(self, data):
        scaled_data = self.scaler.fit_transform(data.values.reshape(-1, 1))
        x, y = [], []
        for i in range(self.sequence_length, len(scaled_data)):
            x.append(scaled_data[i-self.sequence_length:i, 0])
            y.append(scaled_data[i, 0])
        return np.array(x), np.array(y)

    def build_model(self, input_shape):
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(units=1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        self.model = model
        return model

    def train(self, x_train, y_train, epochs=1, batch_size=32):
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
        self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size)

    def predict(self, last_sequence):
        scaled_sequence = self.scaler.transform(last_sequence.reshape(-1, 1))
        x_input = np.array([scaled_sequence])
        x_input = np.reshape(x_input, (x_input.shape[0], x_input.shape[1], 1))
        prediction = self.model.predict(x_input)
        return self.scaler.inverse_transform(prediction)[0][0]
