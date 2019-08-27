from keras.models import Sequential;
#from keras.utils.training_utils import multi_gpu_model;
from keras.layers import Dense, LSTM;

def init(size, shape):
    model = Sequential();
    model.add(LSTM(size, input_shape=(shape[1], shape[2])));
    model.add(Dense(size, activation='relu'));
    #model = multi_gpu_model(model, gpus=2);
    model.compile(loss='mse', optimizer='adam');
    model.summary();
    return model;
