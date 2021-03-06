import pandas as pd
import numpy as np
import os
import subprocess
import sys
import time
import utils
from datetime import datetime, timedelta

CWD = os.path.dirname(os.path.abspath(__file__))

XLS_PATH = os.path.join(CWD, 'xlsFiles')
WT = os.path.join('WT', 'FILES')
TT = os.path.join('TT', 'FILES')

days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
TIMESLOT_SIZE = 15 #15 minutes
TIMESLOT_DIMENSION = int(24*(60/TIMESLOT_SIZE)) #hour * timeslot count per hour

def makeTarget(files):
    std = datetime.now() - timedelta(days=14)
    string = '63_' + std.strftime("%Y-%m-%d") + '_5413.xls'
    targetFiles = []
    for file in files:
        if(file > string):
            targetFiles.append(file)
    files = list(set(files) - set(targetFiles))
    return files, targetFiles

def mvSomefiles(files, fromDir, toDir):
    for file in files:
        subprocess.call(['mv', os.path.join(fromDir, file), os.path.join(toDir, file)])

#filePath or fileObject;
def makeADT(fileName):
    df = pd.read_excel(os.path.join(XLS_PATH, fileName + '.xls'), index_col=False)
    df = df.to_numpy()[:, 2:]
    df = pd.DataFrame(data=df)
    
    arrivalIndexes = range(0, df.shape[0], 2)
    departureIndexes = range(1, df.shape[0], 2)
    
    departureFrame = df.loc[departureIndexes]
    arrivalFrame = df.loc[arrivalIndexes]
    
    dpDim = departureFrame.shape
    dpList = departureFrame.astype(str).to_numpy().flatten()
    arDim = arrivalFrame.shape
    arList = arrivalFrame.astype(str).to_numpy().flatten()
    
    dpList = [utils.strToUnixTimestamp(elem) for elem in dpList]
    arList = [utils.strToUnixTimestamp(elem) for elem in arList]
    
    dpArr = np.array(dpList).reshape(dpDim)
    arArr = np.array(arList).reshape(arDim)
    
    return dpArr, arArr

def makeWT(departure, arrival):
    dpArr = departure
    atArr = arrival
    
    timeslotArr = np.zeros((TIMESLOT_DIMENSION, atArr.shape[1]))
    countArr = np.zeros((TIMESLOT_DIMENSION, atArr.shape[1]))
    result = np.zeros((TIMESLOT_DIMENSION, atArr.shape[1]))
    
    for i, list in enumerate(atArr):
        for j, elem in enumerate(list):
            if(not pd.isnull(elem)):
                if(not pd.isnull(dpArr[i, j])):
                    index = utils.judgeTimeslot(elem)
                    wt = dpArr[i, j] - elem
                    if(wt < 0):
                        wt = dpArr[i, j] + 24*60*60 - elem
                    if(wt > 10000):
                        break
                    timeslotArr[index, j] += wt
                    countArr[index, j] += 1
    for i, list in enumerate(result):
        for j, elem in enumerate(list):
            if(countArr[i][j] != 0):
                result[i][j] = round(timeslotArr[i, j] / countArr[i, j], 2)

    return result


def makeTT(departure, arrival):
    dpArr = departure[:, :-1]
    atArr = arrival[:, 1:]
    
    timeslotArr = np.zeros((TIMESLOT_DIMENSION, atArr.shape[1]))
    countArr = np.zeros((TIMESLOT_DIMENSION, atArr.shape[1]))
    result = np.zeros((TIMESLOT_DIMENSION, atArr.shape[1]))
    
    for i, list in enumerate(atArr):
        for j, elem in enumerate(list):
            if(not pd.isnull(elem)):
                if(not pd.isnull(dpArr[i, j])):
                    index = utils.judgeTimeslot(elem)
                    arriveTime = elem
                    departureTime = dpArr[i, j]
                    tripTime = arriveTime - departureTime
                    if(tripTime < 0 ):
                        arriveTime = arriveTime + 24*60*60
                        tripTime = arriveTime - departureTime
                    if(tripTime > 10000):
                        break
                    timeslotArr[index, j] += tripTime
                    countArr[index, j] += 1

    for i, list in enumerate(result):
        for j, elem in enumerate(list):
            if(countArr[i][j] != 0):
                result[i][j] = round(timeslotArr[i, j] / countArr[i, j], 2)

    return result

def process(xlsFilePath):
    fileName = os.path.basename(xlsFilePath)
#    subprocess.call(['mv', xlsFilePath, os.path.join(XLS_PATH, fileName)])
    fileName = fileName.split('.xls')[0]
    print(fileName)
    dtArr, atArr = makeADT(fileName)
    wtArr = makeWT(dtArr, atArr)
    ttArr = makeTT(dtArr, atArr)
    convertedName, dayType = utils.makeName(fileName)
    print(convertedName)
    
    path = os.path.join(CWD, dayType)
    
    if(os.path.exists(os.path.join(path, WT, convertedName + '.csv')) and os.path.exists(os.path.join(path, TT, convertedName + '.csv'))):
        print("file aleady exists")
        return dayType, convertedName
    
    utils.saveArrToDf(wtArr, os.path.join(path, WT, convertedName + '.csv'))
    utils.saveArrToDf(ttArr, os.path.join(path, TT, convertedName + '.csv'))
    
    print("file saved")

    return dayType, convertedName

if __name__ == "__main__":
    
    files = [f for f in os.listdir(XLS_PATH) if ( (f.endswith('.xls')) and not (f.startswith('.')) )]
    files, targetFiles = makeTarget(files)
    mvSomefiles(targetFiles, XLS_PATH, CWD)
    
    start = time.time()
    for file in files:
        process(os.path.join(XLS_PATH, file))
    mvSomefiles(targetFiles, CWD, XLS_PATH)
    print("upload process : " + str(time.time()-start) + 's')
