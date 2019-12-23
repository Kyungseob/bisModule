import pandas as pd
import numpy as np
import os
import utils
import nn
import utils
import time
import tensorflow as tf

CWD = os.path.dirname(os.path.abspath(__file__))

modelDict = dict()

def initParam(dayType, dirType):
    base = os.path.join(CWD, dayType)
    intPath = os.path.join(base, dirType, 'INT')
    files = [f for f in os.listdir(intPath) if(f.endswith('.csv'))]
    sizeParam = utils.getSizeParam(os.path.join(intPath, files[0]))
    return sizeParam[1], (1,1, sizeParam[1])

def loadModels():
    dayTypes = ['weekday', 'weekend']
    dirs = ['TT', 'WT']
    for dayType in dayTypes:
        modelConfigs = dict()
        for dir in dirs:
            configs = []
            for i in range(3):
                graph = tf.Graph()
                with graph.as_default():
                    session = tf.Session()
                    with session.as_default():
                        size, shape = initParam(dayType, dir)
                        model = nn.init(size, shape)
                        model.load_weights(os.path.join(CWD, dayType, dir, 'MODELS', 'model' + '_' + str(i+1) + '.h5'))
                        configs.append((graph, session, model))
            modelConfigs[dir] = configs
        modelDict[dayType] = modelConfigs

loadModels()

def predict(file, dayType, dirType, intPath):
    sizeParam = utils.getSizeParam(os.path.join(intPath, file))
    print(sizeParam)
    df = pd.read_csv(os.path.join(intPath, file), index_col=False)
    arr = df.to_numpy()
    print(arr.shape)
    all = []
    all.append(arr.flatten().T)
    all = np.array(all)
    result = []
    for i in range(len(sizeParam) - 1):
        part = all[:, sizeParam[i]:sizeParam[i+1]]
        part = np.reshape(part, (part.shape[0], 1, part.shape[1]))
        print(part.shape)
        graph, session, model = modelDict[dayType][dirType][i]
        with graph.as_default():
            with session.as_default():
                pResult = model.predict(part)
                pResult = np.array(pResult)
                pResult = pResult.flatten().T
                result.append(pResult)
    result = np.array(result)
    result = np.reshape(result, (arr.shape[0], arr.shape[1]))
    return result

def interpolate(pred, avgPath):
    df = pd.read_csv(avgPath, index_col=False)
    avg = df.to_numpy()
    for i, list in enumerate(pred):
        for j, elem in enumerate(list):
            if (elem == 0):
                pred[i, j] = avg[i, j]
    return pred

def process(dayType, name):
    base = os.path.join(CWD, dayType)
    TT_INT = os.path.join(base, 'TT', 'INT')
    WT_INT = os.path.join(base, 'WT', 'INT')
    TT_RESULT = os.path.join(base, 'TT', 'RESULT')
    WT_RESULT = os.path.join(base, 'WT', 'RESULT')
    
    fileName = name + '.csv'
    
    baseName = fileName.split('_')[0]
    
    TT_AVG = os.path.join(base, 'TT', 'AVG', baseName + '_AVG.csv')
    WT_AVG = os.path.join(base, 'WT', 'AVG', baseName + '_AVG.csv')
    
    resultName = utils.getNextDate(baseName) + '.csv'
    
    if(os.path.exists(os.path.join(TT_RESULT, resultName)) and os.path.exists(os.path.join(WT_RESULT, resultName))):
        print('predict file aleady exists')
        return resultName
    
    ttPred = predict(fileName, dayType, 'TT', TT_INT)
    wtPred = predict(fileName, dayType, 'WT', WT_INT)
    
    ttIntPred = interpolate(ttPred, TT_AVG)
    wtIntPred = interpolate(wtPred, WT_AVG)
    
    pd.DataFrame(data=ttIntPred).to_csv(os.path.join(TT_RESULT, resultName), index=False)
    pd.DataFrame(data=wtIntPred).to_csv(os.path.join(WT_RESULT, resultName), index=False)
    
    return resultName
