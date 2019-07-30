import pandas as pd;
from datetime import datetime, date;
import time;
import math;

TIMESLOT_SIZE = 15;
days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];

def idxToTime(idx):
    hour = str(int(math.floor(idx/4)));
    minute = str(idx%4 * 15);
    nHour = str(int(math.floor((idx+1)/4)));
    nMinute = str((idx+1)%4 * 15);
    if( len(hour) == 1 ): hour = '0'+hour;
    if( minute == '0' ): minute = minute+'0';
    if( nMinute == '0' ): nMinute = nMinute+'0';
    if( len(nHour) == 1 ): nHour = '0' + nHour;
    return hour + ':' + minute + '~' + nHour + ':' + nMinute;

def makeName(fileName):
    fileName = fileName.split('_')[1];
    splittedDates = fileName.split('-');
    dayType = 'weekday'
    idx = date(int(splittedDates[0]), int(splittedDates[1]), int(splittedDates[2])).weekday();
    if(idx > 4):
        dayType = 'weekend';
    day = days[idx];
    dates = ''.join(splittedDates);
    result  = dates + '_' + day;
    return result, dayType;

def strToUnixTimestamp(str):
    if (pd.isnull(str) or str=='NaT'):
        return float('nan');
    dt = datetime.strptime(str, "%Y-%m-%d %H:%M:%S")
    ts = time.mktime(dt.timetuple());
    return ts;

def judgeTimeslot(date):
    date = timestampToStrDate(date);
    timeStr = date.split(' ')[1];
    splitted = timeStr.split(':');
    hour = int(splitted[0]);
    minute = int(splitted[1]);
    return hour*4 + int(math.floor(minute/TIMESLOT_SIZE));

def strDateToTimestamp(str):
    dateStr = str.split(' ')[1];
    splitted = dateStr.split(':');
    hour = int(splitted[0]);
    minute = int(splitted[1]);
    second = int(splitted[2]);
    return hour*60*60 + minute*60 + second;

def timestampToStrDate(timestamp):
    dtObj = datetime.fromtimestamp(timestamp);
    return dtObj.strftime("%Y-%m-%d %H:%M:%S");

def saveArrToDf(arr, path):
    df = pd.DataFrame(data = arr);
    df.to_csv(path, index=False);

def calcAvgFirst(arr):
    count = 0;
    sum = 0;
    for i in range(arr.shape[0]):
        if(arr[i, 0] != 0 and arr[i,0] < 200):
            sum += arr[i, 0];
            count += 1;
    if(count == 0):
        return False;
    return round(sum/count, 2);

def getSizeParam(file):
    df = pd.read_csv(file, index_col=False);
    dArray = df.as_matrix();
    total = dArray.shape[0] * dArray.shape[1];
    part = total / 6;
    print(dArray.shape, total, part)
    sizeParam = range(0, total, part);
    sizeParam.append(total);
    return sizeParam;

