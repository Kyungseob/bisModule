import pandas as pd;
import numpy as np;
import math;
import os;
import utils;

CWD = os.getcwd();

file = '20180917_MON.csv';

dayType = 'weekday'

base = CWD + '/' + dayType + '/';
WT_RESULT = base + 'WT/RESULT/';
TT_RESULT = base + 'TT/RESULT/';
CARD_STDEV = base + 'CARD_DATA/';
TABLE_DIR = base + 'PRED_TABLE/';

TIMESLOT = 96;
FIRST_TRIP = 0;
LAST_TRIP = 0;
TRIP_COUNT = 0;
MAX_BUS_COUNT = 0;
STOP_COUNT = 0;

def init(first, last, tripCount, busCount, stopCount):
    global FIRST_TRIP, LAST_TRIP, TRIP_COUNT, MAX_BUS_COUNT, STOP_COUNT;
    FIRST_TRIP = first;
    LAST_TRIP = last;
    TRIP_COUNT = tripCount;
    MAX_BUS_COUNT = busCount;
    STOP_COUNT = stopCount;

init(4*60*60 + 10*60, 22*60*60 + 30*60, 124, 27, 99);
DEFAULT_PERIOD = float(LAST_TRIP-FIRST_TRIP) / float(TRIP_COUNT-1);
PERIOD_MAP = np.zeros((TRIP_COUNT));
ADDED_WEIGHT = 0.0;
TIME_MAP = np.zeros((1, STOP_COUNT+1));
START_MAP = np.zeros((TRIP_COUNT));

TT_PREDICTION_MAP = pd.read_csv(TT_RESULT + file, index_col=False).to_numpy()[:, :];
WT_PREDICTION_MAP = pd.read_csv(WT_RESULT + file, index_col=False).to_numpy()[:, :];

WEIGHT_MAP = pd.read_csv(CARD_STDEV, index_col=False).to_numpy()[:, 6:7].flatten();
WEIGHT_MAP = np.concatenate([np.zeros(16), WEIGHT_MAP, np.zeros(5)]);

TEST_WEIGHT = 0.0;

def getPeriod(tripIdx):
    return PERIOD_MAP[tripIdx];

def getWeight(sec):
    return WEIGHT_MAP[secToIdx(sec)];

def calcPeriod(startTime):
    global PERIOD_MAP;
    sumOfNegative = 0;
    sumOfPositive = 0;
    for i in range(TRIP_COUNT):
        PERIOD_MAP[i] = getWeight(startTime+DEFAULT_PERIOD*i);
        if(i == 0 or i == TRIP_COUNT-1):
            PERIOD_MAP[i] = 0;
        if(PERIOD_MAP[i] < 0):
            sumOfNegative += PERIOD_MAP[i];
        else :
            sumOfPositive += PERIOD_MAP[i];
    sumOfAll = 0;
    for i in range(TRIP_COUNT):
        if (PERIOD_MAP[i] > 0):
            PERIOD_MAP[i] = -sumOfNegative * PERIOD_MAP[i]/sumOfPositive;
        sumOfAll += PERIOD_MAP[i];
    
    for i in range(TRIP_COUNT):
        PERIOD_MAP[i] = PERIOD_MAP[i] * 60;

    PERIOD_MAP = PERIOD_MAP[1:];
    return ;

def changePeriod(tripIdx, val):
    remain = TRIP_COUNT - (tripIdx+1) -1;
    global ADDED_WEIGHT;
    ADDED_WEIGHT += val;
    calibrate = -val/(remain);
    for i in range(remain):
        PERIOD_MAP[tripIdx+i] += calibrate;

def ttPredictionValue(sec, idx):
    secIdx = secToIdx(sec);
    val = TT_PREDICTION_MAP[secIdx, idx];
    if (val == 0):
        upperIdx = secIdx - 1;
        downIdx = secIdx + 1;
        if(downIdx > 95):
            downIdx = downIdx - 96;
        upperVal = TT_PREDICTION_MAP[upperIdx, idx];
        downVal = TT_PREDICTION_MAP[downIdx, idx];
        if (upperVal != 0 and downVal != 0):
            val = (upperVal + downVal)/2;
        elif (upperVal == 0 and downVal != 0):
            val = downVal;
        else:
            val = upperVal;
    return val;

def wtPredictionValue(sec, idx):
    secIdx = secToIdx(sec);
    val = WT_PREDICTION_MAP[secIdx, idx];
    if (val == 0):
        upperIdx = secIdx - 1;
        downIdx = secIdx + 1;
        if(downIdx > 95):
            downIdx = downIdx - 96;
        upperVal = WT_PREDICTION_MAP[upperIdx, idx];
        downVal = WT_PREDICTION_MAP[downIdx, idx];
        if (upperVal != 0 and downVal != 0):
            val = (upperVal + downVal)/2;
        elif (upperVal == 0 and downVal != 0):
            val = downVal;
        else:
            val = upperVal;
    return val;

def createTrip(startTime, tripIdx, flag):
    global TIME_MAP;
    sTimes = range(int(startTime)-180, int(startTime)+180);
    timeSeries = [];
    costSeries = [];
    if(startTime == FIRST_TRIP):
        TIME_MAP[tripIdx,0] = startTime;
        for i in range(1, STOP_COUNT):
            temp = [];
            TIME_MAP[tripIdx, i] = TIME_MAP[tripIdx, i - 1] + ttPredictionValue(TIME_MAP[tripIdx, i - 1], i-1) + wtPredictionValue(TIME_MAP[tripIdx, i - 1], i);
        TIME_MAP[tripIdx, STOP_COUNT] = TIME_MAP[tripIdx, STOP_COUNT-1] + 15.0 * 60.0;
        return ;
    temp = np.zeros((1, STOP_COUNT+1));
    TIME_MAP = np.concatenate((TIME_MAP, temp), axis=0)
    if(tripIdx == 123 or flag):
        TIME_MAP[tripIdx,0] = startTime;
        for i in range(1, STOP_COUNT):
            temp = [];
            TIME_MAP[tripIdx, i] = TIME_MAP[tripIdx, i - 1] + ttPredictionValue(TIME_MAP[tripIdx, i - 1], i-1) + wtPredictionValue(TIME_MAP[tripIdx, i - 1], i);
        TIME_MAP[tripIdx, STOP_COUNT] = TIME_MAP[tripIdx, STOP_COUNT-1] + 15.0 * 60.0;
        return ;
    for sTime in sTimes:
        cost = 0;
        temp = [];
        temp.append(sTime);
        for i in range(1, STOP_COUNT):
            temp.append(temp[i-1] + ttPredictionValue(temp[i-1], i-1) + wtPredictionValue(temp[i-1], i-1));
            val = abs(temp[i] - TIME_MAP[tripIdx - 1, i] - (DEFAULT_PERIOD + getPeriod(tripIdx-1)))
            cost = cost + val*val;
        timeSeries.append(temp);
        costSeries.append(cost);
    idx = costSeries.index(min(costSeries));
    global TEST_WEIGHT;
    TEST_WEIGHT += (idx-180);
    for i, elem in enumerate(timeSeries[idx]):
        TIME_MAP[tripIdx, i] = elem;
    TIME_MAP[tripIdx, STOP_COUNT] = TIME_MAP[tripIdx, STOP_COUNT-1] + 15.0 * 60.0;
    return ;

def concatZero(val):
    if(val < 10):
        return '0' + str(val);
    return str(val);

def parseTimemap():
    wrapper = np.vectorize(secToString);
    return wrapper(TIME_MAP);

def validationMax(time, idx):
    tempMap = TIME_MAP[:idx, :];
    df = pd.DataFrame(data=tempMap);
    df = df[df > time];
    df = df.drop(df.index[df.isnull().all(1)]);
    arr = df.to_numpy()[:idx, :];
    remains = [];
    for i, list in enumerate(arr):
        start = 0.0;
        end = list[STOP_COUNT];
        for j, elem in enumerate(list):
            if (not np.isnan(elem)):
                start=time;
                break;
        remain = end - start;
        remains.append(remain);
    onTripCount = len(remains);
    onReadyCount = MAX_BUS_COUNT - onTripCount;
    sumReadyTime = 0.0;
    if (idx < TRIP_COUNT - MAX_BUS_COUNT):
        for i in range(onReadyCount):
            sumReadyTime += (DEFAULT_PERIOD + getPeriod(idx+i-1));
        ret = 0.0;
        temp = sumReadyTime - remains[0];
        if(temp > 0):
            ret = True;
        else:
            if( abs(temp) > 1):
                ret = -(sumReadyTime - remains[0]);
            else :
                ret = True;
    else:
        ret = True;
    return ret;

calcPeriod(FIRST_TRIP);

START_MAP[0] = FIRST_TRIP;
createTrip(START_MAP[0], 0, False);
for i in range(1, TRIP_COUNT-1):
    START_MAP[i] = TIME_MAP[i-1, 0] + DEFAULT_PERIOD + getPeriod(i-1);
    validate = validationMax(START_MAP[i], i);
    flag = False;
    while(isinstance(validate, float)):
        START_MAP[i] += validate;
        changePeriod(i, validate);
        validate = validationMax(START_MAP[i], i);
        flag = True;
    createTrip(START_MAP[i], i, flag);

START_MAP[TRIP_COUNT-1] = TIME_MAP[TRIP_COUNT-2, 0] + DEFAULT_PERIOD + getPeriod(TRIP_COUNT-2) - TEST_WEIGHT;
createTrip(START_MAP[TRIP_COUNT-1], TRIP_COUNT-1, True);

TIME_DIFF = np.zeros((TIME_MAP.shape[0]-1, STOP_COUNT))
DIFF = np.zeros((TIME_MAP.shape[0]-1, 3));
DIFF = np.array(DIFF, dtype=object);

for i in range(TIME_MAP.shape[0]-1):
    DIFF[i, 0] = secToString(TIME_MAP[i, 0]);
    DIFF[i, 1] = secToString(TIME_MAP[i+1, 0]);
    DIFF[i, 2] = round((TIME_MAP[i+1, 0] - TIME_MAP[i, 0])/60, 0);
    for j in range(STOP_COUNT):
        TIME_DIFF[i, j] = int(round(TIME_MAP[i+1, j] - TIME_MAP[i, j], 0) - (DEFAULT_PERIOD + getPeriod(i)));

avg = 0;
for i in range(TIME_MAP.shape[0]-1):
    avg += TIME_MAP[i+1, 0] - TIME_MAP[i, 0];

for i in range(1, TIME_MAP.shape[0]):
    validationMax(TIME_MAP[i,0], i);

avg = avg / (TIME_MAP.shape[0]-1);

parsedMap = parseTimemap();

fileName = file.split('.csv')[0];

pd.DataFrame(data=DIFF).to_csv(TABLE_DIR + fileName + '_diff.csv', index=False);
pd.DataFrame(data=TIME_DIFF).to_csv(TABLE_DIR + fileName + '_timeDiff.csv', index=False);
pd.DataFrame(data=parsedMap).to_csv(TABLE_DIR + fileName + '_table.csv', index=False);