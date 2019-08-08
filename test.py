days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];

def getDayType(fileName):
    day = fileName.split('_')[1].split('.')[0];
    index = days.index(day);
    if(index < 5):
        return 'weekday'
    return 'weekend';

print(getDayType('123123123_FRI.csv'));

