import tensorflow as tf;
import pandas as pd;
import numpy as np;
import os;
import utils;
import nn;
import utils;
import time;

CWD = os.path.dirname(os.path.abspath(__file__));

modelDict = dict();

def initParam(dirType):
    if(dirType == 'TT'):
	return 2720, (1,1,2720);
    return 2752, (1,1,2752);

def loadModels():
    dayTypes = ['weekday'];
    dirs = ['TT', 'WT'];
    for dayType in dayTypes:
        modelConfigs = dict();
        for dir in dirs:
            configs = [];
            for i in range(3):
                graph = tf.Graph();
                with graph.as_default():
                    session = tf.Session();
                    with session.as_default():
                        size, shape = initParam(dir);
                        model = nn.init(size, shape);
                        model.load_weights(os.path.join(CWD, dayType, dir, 'MODELS', 'model' + '_' + str(i+1) + '.h5'));
                        configs.append((graph, session, model));
            modelConfigs[dir] = configs;
        modelDict[dayType] = modelConfigs;

loadModels();

print(modelDict['weekday']['TT']);

