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

def makeAvg(dayType):
    ttPath = os.path.join(CWD, dayType, TT);
    ttAvgPath = os.path.join(CWD, dayType, TT_AVG);
    wtPath = os.path.join(CWD, dayType, WT);
    wtAvgPath = os.path.join(CWD, dayType, WT_AVG);
    makeAvgSumCount(dayType, wtPath, wtAvgPath);
    makeAvgSumCount(dayType, ttPath, ttAvgPath);

def makeAvgSumCount(dayType, path, avgPath):
    files = [f for f in os.listdir(path) if (f.endswith('.csv'))];
    sumFiles = [f for f in os.listdir(avgPath) if (f.endswith('_SUM.csv'))];
    countFiles = [f for f in os.listdir(avgPath) if (f.endswith('_COUNT.csv'))];
    files.sort(reverse=True);
    sumFiles.sort(reverse=True);
    countFiles.sort(reverse=True);

    date = files[0].split('_')[0];
    sumDate = sumFiles[0].split('_')[0];

    if( int(date) > int(sumDate) ):
    	arr = pd.read_csv(os.path.join(path, files[0]), index_col=False).as_matrix();
    	sumArr = pd.read_csv(os.path.join(avgPath, sumFiles[0]), index_col=False).as_matrix();
    	countArr = pd.read_csv(os.path.join(avgPath, sumFiles[0]), index_col=False).as_matrix();
	result = np.zeros((TIMESLOT_DIMENSION, arr.shape[1]));

    	for i, list in enumerate(arr):
	    for j, elem in enumerate(list):
            	if( elem != 0 ):
                    sumArr[i, j] += elem;
                    countArr[i, j] += 1;
                    if(j == 0 and elem > 300):
                        sumArr[i, j] -= elem;
                        countArr[i, j] -= 1;
	pd.DataFrame(data = countArr).to_csv(os.path.join(avgPath, date + '_COUNT.csv'), index=False)
	pd.DataFrame(data = sumArr).to_csv(os.path.join(avgPath, date + '_SUM.csv'), index=False)
        for i, list in enumerate(result):
            for j, elem in enumerate(list):
    	    	if( countArr[i, j] != 0 ):
                    result[i, j] = result[i,j] / countArr[i, j];

        pd.DataFrame(data=result).to_csv(os.path.join(avgPath, date + '_AVG.csv'), index=False);

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
    file = files[0];
    date = file.split('_')[0];
    avgTT = pd.read_csv(os.path.join(avgPath, date + '_AVG.csv'), index_col=False);
    avgArr = avgTT.as_matrix();
    firstAvg = utils.calcAvgFirst(avgArr);
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
    makeAvg(dayType);
    makeINT(dayType);

if(__name__ == '__main__'):
    start = time.time();
    makeAvg('weekday');
#    makeAvg('weekend');
    makeINT('weekday');
    print('preprocessing process : ' + str(time.time() - start) + 's');
#    makeINT('weekend');
