import os;
import numpy as np;
import pandas as pd;
import utils;
import time;

CWD = os.path.dirname(os.path.abspath(__file__));

TT_INT = os.path.join('TT', 'INT');
WT_INT = os.path.join('WT', 'INT');
TT_AVG = os.path.join('TT', 'AVG');
WT_AVG = os.path.join('WT', 'AVG');
TT = os.path.join('TT', 'FILES');
WT = os.path.join('WT', 'FILES');

TIMESLOT_SIZE = 15;
TIMESLOT_DIMENSION = int(24*(60/TIMESLOT_SIZE)) #hour * timeslot count per hour

def makeAvgTT(dayType):
    ttPath = os.path.join(CWD, dayType, TT);
    avgPath = os.path.join(CWD, dayType, TT_AVG);
    files = [f for f in os.listdir(ttPath) if (f.endswith('.csv'))];
    files.sort(reverse=True);
    date = files[0].split('_')[0];
    df = pd.read_csv(os.path.join(ttPath, files[0]), index_col=False);
    
    result = np.zeros((TIMESLOT_DIMENSION, df.shape[1]));
    count = np.zeros((TIMESLOT_DIMENSION, df.shape[1]));
    
    for file in files:
        df = pd.read_csv(os.path.join(ttPath, file), index_col=False);
        arr = df.as_matrix();
        for i, list in enumerate(arr):
            for j, elem in enumerate(list):
                if( elem != 0 ):
                    result[i, j] += elem;
                    count[i, j] += 1;
                    if(j == 0 and elem > 300):
                        result[i, j] -= elem;
                        count[i, j] -= 1;
    pd.DataFrame(data=count).to_csv(os.path.join(avgPath, date + '_COUNT.csv'), index=False);
    pd.DataFrame(data=result).to_csv(os.path.join(avgPath, date + '_SUM.csv'), index=False);
    for i, list in enumerate(result):
        for j, elem in enumerate(list):
            if( count[i, j] != 0 ):
                result[i, j] = result[i,j] / count[i, j];

    timeSlotCol = [utils.idxToTime(i) for i in range(TIMESLOT_DIMENSION)];
    resultdf = pd.DataFrame(data=result);
    
    resultdf.to_csv(os.path.join(avgPath, date + '_AVG.csv'), index=False);

def makeAvgWT(dayType):
    wtPath = os.path.join(CWD, dayType, WT);
    avgPath = os.path.join(CWD, dayType, WT_AVG);
    files = [f for f in os.listdir(wtPath) if (f.endswith('.csv'))];
    files.sort(reverse=True);
    date = files[0].split('_')[0];
    df = pd.read_csv(os.path.join(wtPath, files[0]), index_col=False);
    
    result = np.zeros((TIMESLOT_DIMENSION, df.shape[1]));
    count = np.zeros((TIMESLOT_DIMENSION, df.shape[1]));
    
    for file in files:
        df = pd.read_csv(os.path.join(wtPath, file), index_col=False);
        arr = df.as_matrix();
        for i, list in enumerate(arr):
            for j, elem in enumerate(list):
                if( elem != 0 ):
                    result[i, j] += elem;
                    count[i, j] += 1;
                    if(j == 0 and elem > 300):
                        result[i, j] -= elem;
                        count[i, j] -= 1;
    pd.DataFrame(data=count).to_csv(os.path.join(avgPath, date + '_COUNT.csv'), index=False);
    pd.DataFrame(data=result).to_csv(os.path.join(avgPath, date + '_SUM.csv'), index=False);
    for i, list in enumerate(result):
        for j, elem in enumerate(list):
            if( count[i, j] != 0 ):
                result[i, j] = result[i,j] / count[i, j];

    timeSlotCol = [utils.idxToTime(i) for i in range(TIMESLOT_DIMENSION)];
    resultdf = pd.DataFrame(data=result);
    resultdf.to_csv(os.path.join(avgPath, date + '_AVG.csv'), index=False);

def makeINT(dayType):
    base = os.path.join(CWD, dayType);
    ttPath = os.path.join(base, TT);
    ttAvgPath = os.path.join(base, TT_AVG);
    ttIntPath = os.path.join(base, TT_INT);
    wtPath = os.path.join(base, WT);
    wtAvgPath = os.path.join(base, WT_AVG);
    wtIntPath = os.path.join(base, WT_INT);
    interpolate(ttPath, ttAvgPath, ttIntPath);
    interpolate(wtPath, wtAvgPath, wtIntPath);

def interpolate(path, avgPath, intPath):
    files = [f for f in os.listdir(path) if (f.endswith('.csv'))];
    files.sort(reverse=True);
    date = files[0].split('_')[0];
    avgTT = pd.read_csv(os.path.join(avgPath, date + '_AVG.csv'), index_col=False);
    avgArr = avgTT.as_matrix();
    firstAvg = utils.calcAvgFirst(avgArr);
    for file in files:
        df = pd.read_csv(os.path.join(path, file), index_col=False);
        arr = df.as_matrix();
        for i, list in enumerate(arr):
            for j, elem in enumerate(list):
                if (elem == 0 or elem > 200):
                    arr[i, j] = round(avgArr[i, j], 2);
                    if(avgArr[i,j] == 0 and j == 0 and i > 15 and i < 91):
                        arr[i, j] = firstAvg;
    
        resultdf = pd.DataFrame(data = arr);
        resultdf.to_csv(os.path.join(intPath, file), index=False);

def process(dayType):
    makeAvgTT(dayType);
    makeAvgWT(dayType);
    makeINT(dayType);

if(__name__ == '__main__'):
    start = time.time();
    makeAvgTT('weekday');
    makeAvgTT('weekend');
    makeAvgWT('weekday');
    makeAvgWT('weekend');
    makeINT('weekday');
    makeINT('weekend');
