import pandas as pd;
import numpy as np;
import math;
import os;
import utils;
import nn;

CWD = os.getcwd();

def train(dayType):
    base = CWD + '/' + dayType + '/';
    tt = base + 'TT/INT/';
    wt = base + 'WT/INT/';
    ttModel = base + 'TT/MODEL/';
    wtModel = base + 'WT/MODEL/';
    files = [f for f in os.listdir(tt) if (f.endswith('.csv'))];
    files.sort();
    sizeParam = utils.getSizeParam(tt + files[0]);
    flatten = [];
    for file in files:
        df = pd.read_csv(tt + file, index_col=False);
        dArray = df.as_matrix();
        flatten.append(dArray.flatten().T);
    flatten = np.array(flatten);
    flatten = np.reshape(flatten, (flatten.shape[0], 1, flatten.shape[1]));
    for i in range(len(sizeParam) -1):
        cutted = flatten[:, :, sizeParam[i]:sizeParam[i+1]];
        cutIdx = int(math.floor(cutted.shape[0]/2));
        trainX = cutted[:cutIdx-1, :, :];
        trainY = cutted[1:cutIdx, :, :];
        trainY = np.reshape(trainY, (cutIdx-1, sizeParam[1]));
        testX = cutted[cutIdx:-1, :, :];
        testY = cutted[cutIdx+1:, :, :];
        testY = np.reshape(testY, (cutIdx-1, sizeParam[1]));
    model = nn.init(sizeParam[1], trainX.shape);
    model.fit(trainX, trainY, epochs=1500, validation_data=(testX, testY), verbose=2);
    model.save_weights(utils.makeDateFileName() + '_' + str(i+1) + '.h5');

train('weekday');
