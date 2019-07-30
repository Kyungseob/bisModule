import os;
import numpy as np;
import pandas as pd;
import utils;

CWD = os.getcwd();

TT_INT = '/TT/INT/';
WT_INT = '/WT/INT/';
TT_AVG = '/TT/AVG/';
WT_AVG = '/WT/AVG/';
TT = '/TT/FILES/';
WT = '/WT/FILES/';

TIMESLOT_SIZE = 15;
TIMESLOT_DIMENSION = int(24*(60/TIMESLOT_SIZE)) #hour * timeslot count per hour

def makeAvgTT(dayType):
    ttPath = CWD + '/' + dayType + '/' + TT;
    avgPath = CWD + '/' + dayType + '/' + TT_AVG;
    files = [f for f in os.listdir(ttPath) if (f.endswith('.csv'))];
    
    df = pd.read_csv(ttPath + files[0], index_col=False);
    
    result = np.zeros((TIMESLOT_DIMENSION, df.shape[1]));
    count = np.zeros((TIMESLOT_DIMENSION, df.shape[1]));
    
    for file in files:
        fileName = file.split('_TT')[0];
        df = pd.read_csv(ttPath + file, index_col=False);
        arr = df.as_matrix();
        for i, list in enumerate(arr):
            for j, elem in enumerate(list):
                if( elem != 0 ):
                    result[i, j] += elem;
                    count[i, j] += 1;
                    if(j == 0 and elem > 300):
                        result[i, j] -= elem;
                        count[i, j] -= 1;
    for i, list in enumerate(result):
        for j, elem in enumerate(list):
            if( count[i, j] != 0 ):
                result[i, j] = result[i,j] / count[i, j];

    timeSlotCol = [utils.idxToTime(i) for i in range(TIMESLOT_DIMENSION)];
    resultdf = pd.DataFrame(data=result);
    resultdf.to_csv(avgPath + 'TT_AVG.csv', index=False);

def makeAvgWT(dayType):
    wtPath = CWD + '/' + dayType + '/' + WT;
    avgPath = CWD + '/' + dayType + '/' + WT_AVG;
    files = [f for f in os.listdir(wtPath) if (f.endswith('.csv'))];
    
    df = pd.read_csv(wtPath + files[0], index_col=False);
    
    result = np.zeros((TIMESLOT_DIMENSION, df.shape[1]));
    count = np.zeros((TIMESLOT_DIMENSION, df.shape[1]));
    
    for file in files:
        fileName = file.split('_TT')[0];
        df = pd.read_csv(wtPath + file, index_col=False);
        arr = df.as_matrix();
        for i, list in enumerate(arr):
            for j, elem in enumerate(list):
                if( elem != 0 ):
                    result[i, j] += elem;
                    count[i, j] += 1;
                    if(j == 0 and elem > 300):
                        result[i, j] -= elem;
                        count[i, j] -= 1;
    for i, list in enumerate(result):
        for j, elem in enumerate(list):
            if( count[i, j] != 0 ):
                result[i, j] = result[i,j] / count[i, j];

    timeSlotCol = [utils.idxToTime(i) for i in range(TIMESLOT_DIMENSION)];
    resultdf = pd.DataFrame(data=result);
    resultdf.to_csv(avgPath + 'WT_AVG.csv', index=False);

def makeINT(dayType):
    base = CWD + '/' + dayType + '/';
    ttPath = base + TT;
    ttAvgPath = base + TT_AVG + 'TT_AVG.csv';
    ttIntPath = base + TT_INT;
    wtPath = base + WT;
    wtAvgPath = base + WT_AVG + 'WT_AVG.csv';
    wtIntPath = base + WT_INT;
    interpolate(ttPath, ttAvgPath, ttIntPath);
    interpolate(wtPath, wtAvgPath, wtIntPath);

def interpolate(path, avgPath, intPath):
    files = [f for f in os.listdir(path) if (f.endswith('.csv'))];
    avgTT = pd.read_csv(avgPath, index_col=False);
    avgArr = avgTT.as_matrix();
    firstAvg = utils.calcAvgFirst(avgArr);
    for file in files:
        df = pd.read_csv(path + file, index_col=False);
        arr = df.as_matrix();
        for i, list in enumerate(arr):
            for j, elem in enumerate(list):
                if (elem == 0 or elem > 200):
                    arr[i, j] = round(avgArr[i, j], 2);
                    if(avgArr[i,j] == 0 and j == 0 and i > 15 and i < 91):
                        arr[i, j] = firstAvg;
    
        resultdf = pd.DataFrame(data = arr);
        resultdf.to_csv(intPath + file, index=False);

makeAvgTT('weekday');
makeAvgWT('weekday');
makeINT('weekday');
