
import subprocess
import os;

CWD = os.getcwd();

XLS_DIR = 'xlsFiles'
TYPE_DIR = ['weekday', 'weekend'];
TIME_NAMES = ['WT', 'TT'];
SUBDIR_NAMES = ['FILES', 'AVG', 'MODELS', 'INT', 'RESULT'];

if(not os.path.isdir(CWD + '/' + XLS_DIR)):
    subprocess.call(['mkdir', CWD + '/' + XLS_DIR]);

for name in TYPE_DIR:
    if(not os.path.isdir(CWD + '/' + name)):
        subprocess.call(['mkdir', name]);
        for timeName in TIME_NAMES:
            if(not os.path.isdir(CWD + '/' + name + '/' + timeName)):
                subprocess.call(['mkdir', CWD + '/' + name + '/' + timeName]);
                for subname in SUBDIR_NAMES:
                    subprocess.call(['mkdir', CWD + '/' + name + '/' + timeName + '/' + subname]);
            else:
                for subname in SUBDIR_NAMES:
                    if(not os.path.isdir(CWD + '/' + name + '/' + timeName + '/' + subname)):
                        subprocess.call(['mkdir', CWD + '/' + name + '/' + timeName + '/' + subname]);
    else:
        for timeName in TIME_NAMES:
            if(not os.path.isdir(CWD + '/' + name + '/' + timeName)):
                subprocess.call(['mkdir', CWD + '/' + name + '/' + timeName]);
                for subname in SUBDIR_NAMES:
                    subprocess.call(['mkdir', CWD + '/' + name + '/' + timeName + '/' + subname]);
            else:
                for subname in SUBDIR_NAMES:
                    if(not os.path.isdir(CWD + '/' + name + '/' + timeName + '/' + subname)):
                        subprocess.call(['mkdir', CWD + '/' + name + '/' + timeName + '/' + subname]);


