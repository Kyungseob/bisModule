import utils
import os, sys

CWD = os.path.dirname(os.path.abspath(__file__))

xlsFilesPath = os.path.join(CWD, 'xlsFiles')
weekdayFilesPath = os.path.join(CWD, 'weekday', 'TT', 'FILES')
weekendFilesPath = os.path.join(CWD, 'weekend', 'TT', 'FILES')

xlsFiles = [f for f in os.listdir(xlsFilesPath) if (f.endswith('.xls') and not f.startswith('.'))]

weekdayFiles = [f for f in os.listdir(weekdayFilesPath) if(f.endswith('.csv'))]
weekendFiles = [f for f in os.listdir(weekendFilesPath) if(f.endswith('.csv'))]

def makeTarget():
    targetFiles = []
    for xlsFile in xlsFiles:
	print(xlsFile)
        fileName = xlsFile.split('.xls')[0]
        fileName, dayType, idx = utils.makeName(fileName)
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

if(len(targetFiles)>0):
    import uploadProcess, preprocessProcess, predictProcess, timetableProcess
    for file in targetFiles:
        dayType, name, idx = uploadProcess.process(os.path.join(xlsFilesPath, file))
        preprocessProcess.process(dayType, name)
        name = predictProcess.process(dayType, name)
        timetableProcess.init(dayType, name, idx)
        print(timetableProcess.process())
