import subprocess
import os

CWD = os.getcwd()

XLS_DIR = 'xlsFiles'
CARD_DIR = 'CARD_DATA'
TABLE_DIR = 'PRED_TABLE'
TYPE_DIR = ['weekday', 'weekend']
TIME_NAMES = ['WT', 'TT']
SUBDIR_NAMES = ['FILES', 'AVG', 'MODELS', 'INT', 'RESULT']

if(not os.path.isdir(os.path.join(CWD, XLS_DIR))):
    subprocess.call(['mkdir', os.path.join(CWD, XLS_DIR)])

for name in TYPE_DIR:
    if(not os.path.isdir(os.path.join(CWD, name))):
        subprocess.call(['mkdir', os.path.join(CWD, name)])
        for timeName in TIME_NAMES:
            if(not os.path.isdir(os.path.join(CWD, name, timeName))):
                subprocess.call(['mkdir', os.path.join(CWD, name, timeName)])
                for subname in SUBDIR_NAMES:
                    subprocess.call(['mkdir', os.path.join(CWD, name, timeName, subname)])
            else:
                for subname in SUBDIR_NAMES:
                    if(not os.path.isdir(os.path.join(CWD, name, timeName, subname))):
                        subprocess.call(['mkdir', os.path.join(CWD, name, timeName, subname)])
    else:
        for timeName in TIME_NAMES:
            if(not os.path.isdir(os.path.join(CWD, name, timeName))):
                subprocess.call(['mkdir', os.path.join(CWD, name, timeName)])
                for subname in SUBDIR_NAMES:
                    subprocess.call(['mkdir', os.path.join(CWD, name, timeName, subname)])
            else:
                for subname in SUBDIR_NAMES:
                    if(not os.path.isdir(os.path.join(CWD, name, timeName, subname))):
                        subprocess.call(['mkdir', os.path.join(CWD, name, timeName, subname)])
    if(not os.path.isdir(os.path.join(CWD, name, CARD_DIR))):
        subprocess.call(['mkdir', os.path.join(CWD, name, CARD_DIR)])
    if(not os.path.isdir(os.path.join(CWD, name, TABLE_DIR))):
        subprocess.call(['mkdir', os.path.join(CWD, name, TABLE_DIR)])

