import pandas as pd;
import numpy as np;
import os;
import utils;
import nn;
import utils;

CWD = os.path.dirname(os.path.abspath(__file__));

def predict(file, mdPath, intPath):
    sizeParam = utils.getSizeParam(os.path.join(intPath, file));
    print(sizeParam);
    df = pd.read_csv(os.path.join(intPath, file), index_col=False);
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
        model.load_weights(os.path.join(mdPath, 'model' + '_' + str(i+1) + '.h5'));
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

def process(dayType):
    base = os.path.join(CWD, dayType);
    TT_INT = os.path.join(base, 'TT', 'INT');
    WT_INT = os.path.join(base, 'WT', 'INT');
    TT_MODEL = os.path.join(base, 'TT', 'MODELS');
    WT_MODEL = os.path.join(base, 'WT', 'MODELS');
    TT_RESULT = os.path.join(base, 'TT', 'RESULT');
    WT_RESULT = os.path.join(base, 'WT', 'RESULT');
    TT_AVG = os.path.join(base, 'TT', 'AVG', 'TT_AVG.csv');
    WT_AVG = os.path.join(base, 'WT', 'AVG', 'WT_AVG.csv');
    
    files = [f for f in os.listdir(TT_INT) if(f.endswith('.csv'))];
    files.sort(reverse=True);
    
    file = files[0];#recent file;
    
    resultName = utils.getNextDate(file.split('_')[0]) + '.csv';
    
    wtPred = predict(file, WT_MODEL, WT_INT);
    ttPred = predict(file, TT_MODEL, TT_INT);
    
    ttIntPred = interpolate(ttPred, TT_AVG);
    wtIntPred = interpolate(wtPred, WT_AVG);
    
    resultName = utils.getNextDate(file.split('_')[0]) + '.csv';
    
    tt = pd.DataFrame(data=ttPred).to_csv(os.path.join(TT_RESULT, resultName), index=False);
    wt = pd.DataFrame(data=wtPred).to_csv(os.path.join(WT_RESULT, resultName), index=False);

if(__name__ == '__main__'):
    base = os.path.join(CWD, 'weekday');
    TT_INT = os.path.join(base, 'TT', 'INT');
    files = [f for f in os.listdir(TT_INT) if(f.endswith('.csv'))];
    files.sort(reverse=True);
    targetFile = files[0];
    dayType = utils.getDayType(targetFile);
    process(dayType);
