import pandas as pd;
import numpy as np;
import os;
import utils;
import nn;

CWD = os.getcwd();

dayType = 'weekday';
base = CWD + '/' + dayType;
TT_INT = base + '/TT/INT/';
WT_INT = base + '/WT/INT/';
TT_MODEL = base + '/TT/MODELS/';
WT_MODEL = base + '/WT/MODELS/';
TT_RESULT = base + '/TT/RESULT/';
WT_RESULT = base + '/WT/RESULT/';
TT_AVG = base + '/TT/AVG/TT_AVG.csv';
WT_AVG = base + '/WT/AVG/WT_AVG.csv';

def predict(file, mdPath, intPath):
    sizeParam = utils.getSizeParam(intPath + file);
    print(sizeParam);
    df = pd.read_csv(intPath + file, index_col=False);
    arr = df.as_matrix();
    print(arr.shape);
    all = [];
    all.append(arr.flatten().T);
    all = np.array(all);
    result = [];
    for i in range(len(sizeParam) - 1):
        part = all[:, sizeParam[i]:sizeParam[i+1]];
        part = np.reshape(part, (part.shape[0], 1, part.shape[1]));
        print(part.shape);
        model = nn.init(sizeParam[1], part.shape);
        model.load_weights(mdPath + '2019-07-30' + '_' + str(i+1) + '.h5');
        pResult = model.predict(part);
        pResult = np.array(pResult);
        pResult = pResult.flatten().T;
        result.append(pResult);
    result = np.array(result);
    result = np.reshape(result, (arr.shape[0], arr.shape[1]));
    return result;

def interpolate(pred, avgPath):
    df = pd.read_csv(avgPath, index_col=False);
    avg = df.as_matrix();
    for i, list in enumerate(pred):
        for j, elem in enumerate(list):
            if (elem == 0):
                pred[i, j] = avg[i, j];
    return pred;

file='20180917_MON.csv';

wtPred = predict(file, WT_MODEL, WT_INT);
ttPred = predict(file, TT_MODEL, TT_INT);

ttIntPred = interpolate(ttPred, TT_AVG);
wtIntPred = interpolate(wtPred, WT_AVG);

tt = pd.DataFrame(data=ttPred).to_csv(TT_RESULT + file, index=False);
wt = pd.DataFrame(data=wtPred).to_csv(WT_RESULT + file, index=False);


