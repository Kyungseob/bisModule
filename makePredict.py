import uploadProcess, preprocessProcess, predictProcess, timetableProcess, utils
import os, sys

CWD = os.getcwd()

xlsFilesPath = os.path.join(CWD, 'xlsFiles')
weekdayFilesPath = os.path.join(CWD, 'weekday', 'TT', 'FILES')
weekendFilesPath = os.path.join(CWD, 'weekend', 'TT', 'FILES')

xlsFiles = [f for f in os.listdir(xlsFilesPath) if (f.endswith('.xls'))]

weekdayFiles = [f for f in os.listdir(weekdayFilesPath) if(f.endswith('.csv'))]
weekendFiles = [f for f in os.listdir(weekendFilesPath) if(f.endswith('.csv'))]

def makeTarget():
    targetFiles = []
    for xlsFile in xlsFiles:
        fileName = xlsFile.split('.xls')[0]
        fileName, dayType = utils.makeDateFileName(fileName)
        flag = False
        if(dayType == 'weekday'):
            flag = fileName + '.csv' in weekdayFiles
        else:
            flag = fileName + '.csv' in weekendFiles
        if(not flag):
            targetFiles.append(xlsFile)
    print(targetFiles)
    return targetFiles

targetFiles = makeTarget()
targetFiles.sort()
for file in targetFiles:
    dayType, name = uploadProcess.process(os.path.join(xlsFilesPath, file))
    preprocessProcess.process(dayType, name)
    name = predictProcess.process(dayType, name)
    timetableProcess.init(dayType, name)
    print(timetableProcess.process())
