import pandas as pd
import numpy as np
import math
import os
import utils
import time

CWD = os.path.dirname(os.path.abspath(__file__))
TIMESLOT = 96 # 15miniture for each slot

def init(dayType, name, idx):
    if(dayType == 'weekday'):
        internalInit(4*60*60 + 20*60, 23*60*60 + 10*60, 156, 27, 86, dayType, name)
    elif(idx == 6):
        internalInit(4*60*60 + 20*60, 23*60*60 + 10*60, 136, 27, 86, dayType, name)
    else:
        internalInit(4*60*60 + 20*60, 23*60*60 + 10*60, 112, 27, 86, dayType, name)

def internalInit(first, last, tripCount, busCount, stopCount, dayType, name):
    global FIRST_TRIP, LAST_TRIP, TRIP_COUNT, MAX_BUS_COUNT, STOP_COUNT, DEFAULT_PERIOD, ADDED_WEIGHT, TEST_WEIGHT, WEIGHT_MAP, TABLE_DIR, PERIOD_MAP, TIME_MAP, START_MAP, TT_PREDICTION_MAP, WT_PREDICTION_MAP, file
    base = os.path.join(CWD, dayType)
    WT_RESULT = os.path.join(base, 'WT', 'RESULT')
    TT_RESULT = os.path.join(base, 'TT', 'RESULT')
    CARD_STDEV = os.path.join(base, 'CARD_DATA')
    TABLE_DIR = os.path.join(base, 'PRED_TABLE')
    TEST_WEIGHT = 0.0
    ADDED_WEIGHT = 0.0
    
    FIRST_TRIP = first
    LAST_TRIP = last
    TRIP_COUNT = tripCount
    MAX_BUS_COUNT = busCount
    STOP_COUNT = stopCount
    DEFAULT_PERIOD = float(LAST_TRIP - FIRST_TRIP) / float(TRIP_COUNT - 1)
    
    file = name
    
    PERIOD_MAP = np.zeros((TRIP_COUNT))
    TIME_MAP = np.zeros((1, STOP_COUNT + 1))
    START_MAP = np.zeros((TRIP_COUNT))
    TT_PREDICTION_MAP = pd.read_csv(os.path.join(TT_RESULT, file), index_col=False).to_numpy()[:, :]
    WT_PREDICTION_MAP = pd.read_csv(os.path.join(WT_RESULT, file), index_col=False).to_numpy()[:, :]
    WEIGHT_MAP = pd.read_csv(os.path.join(CARD_STDEV, dayType + '_dev.csv'), index_col=False).to_numpy().flatten()
    WEIGHT_MAP = np.concatenate([np.zeros(16), WEIGHT_MAP, np.zeros(5)])


def getPeriod(tripIdx):
    return PERIOD_MAP[tripIdx]

def getWeight(sec):
    return WEIGHT_MAP[utils.secToIdx(sec)]

def calcPeriod(startTime):
    global PERIOD_MAP
    sumOfNegative = 0
    sumOfPositive = 0
    for i in range(TRIP_COUNT):
        PERIOD_MAP[i] = getWeight(startTime+DEFAULT_PERIOD*i)
        if(i == 0 or i == TRIP_COUNT-1):
            PERIOD_MAP[i] = 0
        if(PERIOD_MAP[i] < 0):
            sumOfNegative += PERIOD_MAP[i]
        else :
            sumOfPositive += PERIOD_MAP[i]
    sumOfAll = 0
    for i in range(TRIP_COUNT):
        if (PERIOD_MAP[i] > 0):
            PERIOD_MAP[i] = -sumOfNegative * PERIOD_MAP[i]/sumOfPositive
        sumOfAll += PERIOD_MAP[i]
    
    for i in range(TRIP_COUNT):
        PERIOD_MAP[i] = PERIOD_MAP[i] * 60

    PERIOD_MAP = PERIOD_MAP[1:]
    return

def changePeriod(tripIdx, val):
    remain = TRIP_COUNT - (tripIdx+1) -1
    global ADDED_WEIGHT
    ADDED_WEIGHT += val
    calibrate = -val/(remain)
    for i in range(remain):
        PERIOD_MAP[tripIdx+i] += calibrate

def predictionValue(map, sec, idx):
    secIdx = utils.secToIdx(sec)
    val = map[secIdx, idx]
    if (val == 0):
        upperIdx = secIdx - 1
        downIdx = secIdx + 1
        if(downIdx > TIMESLOT - 1):
            downIdx = downIdx - TIMESLOT
        upperVal = map[upperIdx, idx]
        downVal = map[downIdx, idx]
        if (upperVal != 0 and downVal != 0):
            val = (upperVal + downVal)/2
        elif (upperVal == 0 and downVal != 0):
            val = downVal
        else:
            val = upperVal
    return val

def createTrip(startTime, tripIdx, flag):
    global TIME_MAP
    sTimes = range(int(startTime)-180, int(startTime)+180, 30)
    timeSeries = []
    costSeries = []
    if(tripIdx != 0):
        temp = np.zeros((1, STOP_COUNT+1))
        TIME_MAP = np.concatenate((TIME_MAP, temp), axis=0)
    if(startTime == FIRST_TRIP):
        TIME_MAP[tripIdx,0] = startTime
        for i in range(1, STOP_COUNT):
            temp = []
            TIME_MAP[tripIdx, i] = TIME_MAP[tripIdx, i - 1] + predictionValue(TT_PREDICTION_MAP, TIME_MAP[tripIdx, i - 1], i-1) + predictionValue(WT_PREDICTION_MAP, TIME_MAP[tripIdx, i - 1], i)
        TIME_MAP[tripIdx, STOP_COUNT] = TIME_MAP[tripIdx, STOP_COUNT-1] + 15.0 * 60.0
        return
    if(flag):
        TIME_MAP[tripIdx,0] = startTime
        for i in range(1, STOP_COUNT):
            temp = []
            TIME_MAP[tripIdx, i] = TIME_MAP[tripIdx, i - 1] + predictionValue(TT_PREDICTION_MAP, TIME_MAP[tripIdx, i - 1], i-1) + predictionValue(WT_PREDICTION_MAP, TIME_MAP[tripIdx, i - 1], i)
        TIME_MAP[tripIdx, STOP_COUNT] = TIME_MAP[tripIdx, STOP_COUNT-1] + 15.0 * 60.0
        return
    for sTime in sTimes:
        cost = 0
        temp = []
        temp.append(sTime)
        for i in range(1, STOP_COUNT):
            temp.append(temp[i-1] + predictionValue(TT_PREDICTION_MAP, temp[i-1], i-1) + predictionValue(WT_PREDICTION_MAP, temp[i-1], i-1))
            val = abs(temp[i] - TIME_MAP[tripIdx - 1, i] - (DEFAULT_PERIOD + getPeriod(tripIdx-1)))
            cost = cost + val*val
        timeSeries.append(temp)
        costSeries.append(cost)
    idx = costSeries.index(min(costSeries))
    global TEST_WEIGHT
    TEST_WEIGHT += ((idx-6)*30)
    for i, elem in enumerate(timeSeries[idx]):
        TIME_MAP[tripIdx, i] = elem
    TIME_MAP[tripIdx, STOP_COUNT] = TIME_MAP[tripIdx, STOP_COUNT-1] + 15.0 * 60.0
    return

def concatZero(val):
    if(val < 10):
        return '0' + str(val)
    return str(val)

def parseTimemap():
    wrapper = np.vectorize(utils.secToString)
    return wrapper(TIME_MAP)

def validationMax(time, idx):
    tempMap = TIME_MAP[:idx, :]
    df = pd.DataFrame(data=tempMap)
    df = df[df > time]
    df = df.drop(df.index[df.isnull().all(1)])
    arr = df.to_numpy()[:idx, :]
    remains = []
    for i, list in enumerate(arr):
        start = 0.0
        end = list[STOP_COUNT]
        for elem in list:
            if (not np.isnan(elem)):
                start=time
                break
        remain = end - start
        remains.append(remain)
    onTripCount = len(remains)
    onReadyCount = MAX_BUS_COUNT - onTripCount
    sumReadyTime = 0.0
    if (idx < TRIP_COUNT - MAX_BUS_COUNT):
        for i in range(onReadyCount):
            sumReadyTime += (DEFAULT_PERIOD + getPeriod(idx+i-1))
        ret = 0.0
        temp = sumReadyTime - remains[0]
        if(temp > 0):
            ret = True
        else:
            if( abs(temp) > 1):
                ret = -(sumReadyTime - remains[0])
            else :
                ret = True
    else:
        ret = True
    return ret

def process():
    fileName = file.split('.csv')[0]
    if(os.path.exists(os.path.join(TABLE_DIR, fileName + '_table.csv'))):
        print('table already exists')
        return os.path.join(TABLE_DIR, fileName + '_table.csv')
    calcPeriod(FIRST_TRIP)
    START_MAP[0] = FIRST_TRIP
    createTrip(START_MAP[0], 0, False)
    START_MAP[1] = FIRST_TRIP
    createTrip(START_MAP[1], 1, True)
    for i in range(2, TRIP_COUNT-1):
        START_MAP[i] = TIME_MAP[i-1, 0] + DEFAULT_PERIOD + getPeriod(i-1)
        validate = validationMax(START_MAP[i], i)
        flag = False
        while(isinstance(validate, float)):
            START_MAP[i] += validate
            changePeriod(i, validate)
            validate = validationMax(START_MAP[i], i)
            flag = True
        createTrip(START_MAP[i], i, flag)
    START_MAP[i+1] = LAST_TRIP
    createTrip(LAST_TRIP, i+1, True)

    #START_MAP[TRIP_COUNT-1] = TIME_MAP[TRIP_COUNT-2, 0] + DEFAULT_PERIOD + getPeriod(TRIP_COUNT-2) - TEST_WEIGHT
    #createTrip(START_MAP[TRIP_COUNT-1], TRIP_COUNT-1, True)

    TIME_DIFF = np.zeros((TIME_MAP.shape[0]-1, STOP_COUNT))
    DIFF = np.zeros((TIME_MAP.shape[0]-1, 3))
    DIFF = np.array(DIFF, dtype=object)

    for i in range(TIME_MAP.shape[0]-1):
        DIFF[i, 0] = utils.secToString(TIME_MAP[i, 0])
        DIFF[i, 1] = utils.secToString(TIME_MAP[i+1, 0])
        DIFF[i, 2] = round((TIME_MAP[i+1, 0] - TIME_MAP[i, 0])/60, 0)
        for j in range(STOP_COUNT):
            TIME_DIFF[i, j] = int(round(TIME_MAP[i+1, j] - TIME_MAP[i, j], 0) - (DEFAULT_PERIOD + getPeriod(i)))

    avg = 0
    for i in range(TIME_MAP.shape[0]-1):
        avg += TIME_MAP[i+1, 0] - TIME_MAP[i, 0]

    for i in range(1, TIME_MAP.shape[0]):
        validationMax(TIME_MAP[i,0], i)

    avg = avg / (TIME_MAP.shape[0]-1)

    parsedMap = parseTimemap()

    pd.DataFrame(data=DIFF).to_csv(os.path.join(TABLE_DIR, fileName + '_diff.csv'), index=False)
    pd.DataFrame(data=TIME_DIFF).to_csv(os.path.join(TABLE_DIR, fileName + '_timeDiff.csv'), index=False)
    pd.DataFrame(data=parsedMap).to_csv(os.path.join(TABLE_DIR, fileName + '_table.csv'), index=False)
    print('table file saved')

    return os.path.join(TABLE_DIR, fileName + '_table.csv')

