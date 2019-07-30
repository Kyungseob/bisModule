import pandas as pd;
import numpy as np;
import math;
import os;
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import TimeDistributed

param = [0, 1568, 3136, 4704, 6272, 7840, 9408];
CWD = os.getcwd();

files = [f for f in os.listdir(CWD) if (f.endswith('_INT.csv'))];

flatten=[];
for file in files:
	df = pd.read_csv(file, index_col=False);
	dArray = df.as_matrix();
	print(dArray.shape);
	flatten.append(dArray.flatten().T);

flatten = np.array(flatten);
print(flatten.shape)
flatten = np.reshape(flatten, (flatten.shape[0], 1, flatten.shape[1]));
for i in range(len(param) -1):
	cutted = flatten[:, :, param[i]:param[i+1]];
	cutIdx = int(math.floor(cutted.shape[0]/2));
	trainX = cutted[:cutIdx-1, :, :];
	trainY = cutted[1:cutIdx, :, :];
	trainY = np.reshape(trainY, (cutIdx-1, 1568));
	testX = cutted[cutIdx:-1, :, :];
	testY = cutted[cutIdx+1:, :, :];
	testY = np.reshape(testY, (cutIdx-1, 1568));
	print(trainX.shape, trainY.shape, testX.shape, testY.shape);
	
	model = Sequential();
	model.add(LSTM(1568, input_shape=(trainX.shape[1], trainX.shape[2])));
	model.add(Dense(1568, activation='relu'));
	model.compile(loss='mse', optimizer='adam');
	model.summary();
	
	model.fit(trainX, trainY, epochs=1500, validation_data=(testX, testY), verbose=2);
	
	testDf = pd.read_csv('20190515_WED_TT.csv', index_col=False);
	test = testDf.as_matrix();
	fTest = [];
	fTest.append(test.flatten().T);
	fTest = np.array(fTest);
	fTest = np.reshape(fTest, (fTest.shape[0], 1, fTest.shape[1]));
	fTest = fTest[:,:, param[i]:param[i+1]];
	Yhat = model.predict(fTest);
	
	Yhat = np.reshape(Yhat, (16, 98));
	pd.DataFrame(data=Yhat).to_csv('tt_result_'+ str(i+1) +'.csv', index=False);
	print(Yhat)
	print(Yhat.shape)
