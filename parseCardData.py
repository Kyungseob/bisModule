import os;
import sys;
import pandas as pd;
import numpy as np;
import utils;
import math;

#example script python parsedCardData.py targetFile.xls;

TIMESLOT_SIZE = 15;
TIMESLOT_DIMENSION = int(24*(60/TIMESLOT_SIZE)) #hour * timeslot count per hour
WEIGHT= 1.4;

def toTimeslot(date):
    timeStr = date.split(' ')[1];
    splitted = timeStr.split(':');
    hour = int(splitted[0]);
    minute = int(splitted[1]);
    return hour*4 + int(math.floor(minute/TIMESLOT_SIZE));

CWD = os.getcwd()

weekdayCardPath = os.path.join(CWD, 'weekday', 'CARD_DATA');
weekendCardPath = os.path.join(CWD, 'weekend', 'CARD_DATA');

df = pd.read_excel(sys.argv[1]);
dates = df.iloc[1:, 0].as_matrix().tolist();
dates = list(set(dates));
dates.sort();

for date in dates:
    resultDf = df.loc[df[df.columns.values[0]] == date];
    resultDf = resultDf.dropna();
    resultDf = resultDf.sort_values(by=[df.columns.values[5]])
    resultDf.drop(df.columns[[0, 1, 2, 3, 4, 12, 13, 14, 15, 16, 17, 18, 19]], axis=1, inplace=True);
    resultDf = resultDf.reset_index(drop=True);
    name = date.encode('ascii', 'ignore');
    resultDf.to_csv(os.path.join(CWD, utils.judgeDaytype(name), 'CARD_DATA', name+'_card.csv'), header=False, index=False);

def makeAvg(path):
    files = [f for f in os.listdir(path) if (f.endswith('_card.csv'))];
    sum = np.zeros((TIMESLOT_DIMENSION, 5));
    countArr = np.zeros((TIMESLOT_DIMENSION));
    avg = np.zeros((TIMESLOT_DIMENSION, 5));
    for file in files:
        arr = pd.read_csv(os.path.join(path, file), index_col=False).as_matrix();
        for i, list in enumerate(arr):
            index = toTimeslot(list[0]);
            for j in range(5):
                sum[index, j] += list[j+2];
            countArr[index] += 1;

    for i, list in enumerate(sum):
        if(countArr[i] != 0):
            for j in range(5):
                avg[i, j] = int(list[j]/countArr[i]);
    return avg;

def makeDev(path, dayType):
    avgArr = pd.read_csv(os.path.join(path, dayType + '_avg.csv'), index_col=False).as_matrix()[:, 2:3];
    avgArr = avgArr.flatten();
    avgArr = np.delete(avgArr, np.where(avgArr == 0.0), axis=0).tolist();

    count = len(avgArr);

    sumOfAll = sum(avgArr);
    avg = sumOfAll / count;

    squaredSum = 0;
    for elem in avgArr:
        temp = (elem - avg)
        squaredSum += temp*temp;

    stdev = math.sqrt(squaredSum / count-1);

    dev = [];
    for elem in avgArr:
        dev.append(WEIGHT*(elem - avg)/stdev);

    dev = np.array(dev);
    dev = np.reshape(dev, (len(dev), 1));
    return dev;

avgOfWeekday = makeAvg(weekdayCardPath);
avgOfWeekend = makeAvg(weekendCardPath);

pd.DataFrame(data = avgOfWeekday).to_csv(os.path.join(weekdayCardPath, 'weekday_avg.csv'), index=False, header=False);
pd.DataFrame(data = avgOfWeekend).to_csv(os.path.join(weekendCardPath, 'weekend_avg.csv'), index=False, header=False);

weekdayDev = makeDev(weekdayCardPath, 'weekday');
weekendDev = makeDev(weekendCardPath, 'weekend');

pd.DataFrame(data = weekdayDev).to_csv(os.path.join(weekdayCardPath, 'weekday_dev.csv'), index=False, header=False);
pd.DataFrame(data = weekendDev).to_csv(os.path.join(weekendCardPath, 'weekend_dev.csv'), index=False, header=False);
