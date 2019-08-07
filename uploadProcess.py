import pandas as pd;
import numpy as np;
import os;
import subprocess;
import sys;
import time;
import utils;

CWD = os.path.abspath(__file__);

XLS_PATH = CWD + '/' + 'xlsFiles';
WT = '/WT/FILES/'
TT = '/TT/FILES/'

days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
TIMESLOT_SIZE = 15; #15 minutes;
TIMESLOT_DIMENSION = int(24*(60/TIMESLOT_SIZE)) #hour * timeslot count per hour

#filePath or fileObject;
def makeADT(fileName):
    df = pd.read_excel(XLS_PATH + '/' + fileName + '.xls', index_col=False);
    df = df.as_matrix()[:, 2:];
    df = pd.DataFrame(data=df);

    arrivalIndexes = range(0, df.shape[0], 2);
    departureIndexes = range(1, df.shape[0], 2);
        
    departureFrame = df.loc[departureIndexes];
    arrivalFrame = df.loc[arrivalIndexes];

    dpDim = departureFrame.shape;
    dpList = departureFrame.astype(str).as_matrix().flatten();
    arDim = arrivalFrame.shape;
    arList = arrivalFrame.astype(str).as_matrix().flatten();
    
    dpList = [utils.strToUnixTimestamp(elem) for elem in dpList];
    arList = [utils.strToUnixTimestamp(elem) for elem in arList];
    
    dpArr = np.array(dpList).reshape(dpDim);
    arArr = np.array(arList).reshape(arDim);
    
    return dpArr, arArr;

def makeWT(departure, arrival):
    dpArr = departure;
    atArr = arrival;

    timeslotArr = np.zeros((TIMESLOT_DIMENSION, atArr.shape[1]));
    countArr = np.zeros((TIMESLOT_DIMENSION, atArr.shape[1]));
    result = np.zeros((TIMESLOT_DIMENSION, atArr.shape[1]));

    for i, list in enumerate(atArr):
        for j, elem in enumerate(list):
            if(not pd.isnull(atArr[i, j])):
                if(not pd.isnull(dtArr[i, j])):
                    index = utils.judgeTimeslot(atArr[i, j]);
                    wt = dpArr[i, j] - atArr[i, j];
                    if(wt < 0):
                        wt = dpArr[i, j] + 24*60*60 - atArr[i, j];
                    if(wt > 10000):
                        break;
                    timeslotArr[index, j] += wt;
                    countArr[index, j] += 1;
    for i, list in enumerate(result):
        for j, elem in enumerate(list):
            if(countArr[i][j] != 0):
                result[i][j] = round(timeslotArr[i, j] / countArr[i, j], 2);

    return result;


def makeTT(departure, arrival):
    dpArr = departure[:, :-1];
    atArr = arrival[:, 1:];
    
    timeslotArr = np.zeros((TIMESLOT_DIMENSION, atArr.shape[1]));
    countArr = np.zeros((TIMESLOT_DIMENSION, atArr.shape[1]));
    result = np.zeros((TIMESLOT_DIMENSION, atArr.shape[1]));
    
    for i, list in enumerate(atArr):
        for j, elem in enumerate(list):
            if(not pd.isnull(atArr[i, j])):
                if(not pd.isnull(dtArr[i, j])):
                    index = utils.judgeTimeslot(atArr[i, j]);
                    arriveTime = atArr[i, j];
                    departureTime = dtArr[i, j];
                    tripTime = arriveTime - departureTime;
                    if(tripTime < 0 ):
                        arriveTime = arriveTime + 24*60*60;
                        tripTime = arriveTime - departureTime;
                    if(tripTime > 10000):
                        break;
                    timeslotArr[index, j] += tripTime;
                    countArr[index, j] += 1;

    for i, list in enumerate(result):
        for j, elem in enumerate(list):
            if(countArr[i][j] != 0):
                result[i][j] = round(timeslotArr[i, j] / countArr[i, j], 2);

    return result;

def upload(xlsFile):
    files = [f for f in os.listdir(XLS_PATH) if (f.endswith('.xls'))];

    for file in files:
        fileName = file.split('.xls')[0];
        dtArr, atArr = makeADT(fileName);
        wtArr = makeWT(dtArr, atArr);
        ttArr = makeTT(dtArr, atArr);
        convertedName, dayType = utils.makeName(fileName);

        path = CWD + '/' + dayType;

        utils.saveArrToDf(wtArr, path + WT + convertedName + '.csv');
        utils.saveArrToDf(ttArr, path + TT + convertedName + '.csv');

def test():
    print(CWD);
