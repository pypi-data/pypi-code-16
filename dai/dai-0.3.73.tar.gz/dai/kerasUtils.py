import keras
from keras import backend as K
import time
import os
import datetime
import numpy as np
import re
import traceback
from random import randint

from taskProcessors import ProcessTaskProcessor

def parseTrainingProgress(self, line):
    try:
        line = line.replace('\b','')
        # print(line[:250])
        updateDict = {}
        epochList = re.findall(r'Epoch (\d+)\/(\d+)', line)
        if len(epochList)>0:
            self.currentEpoch = int(epochList[-1][0])
            self.totalEpoch = int(epochList[-1][1])
            self.task.set({'status.stage':'Epoch '+epochList[-1][0]+'/'+epochList[-1][1],
                        'output.current_epoch': self.currentEpoch,
                        'output.total_epoch': self.totalEpoch
            })

        progressList = re.findall(r'(\d+)\/(\d+) \[', line)
        if len(progressList)>0:
            prog = int(float(progressList[-1][0])/float(progressList[-1][1])*100.0)
            updateDict['status.progress'] = prog

        etaList = re.findall(r' - ETA: (\d+)s', line)
        if len(etaList) >0:
            mDict = {}
            for m in self.metrics:
                s = re.findall(r' - '+m+': ([-+]?\d*\.\d+|\d+)', line)
                if len(s)>0:
                    mDict[m] = float(s[-1])
            updateDict['output.current_metrics'] = mDict

        totalTimeList = re.findall(r' - (\d+)s', line)
        if len(totalTimeList) >0:
            mDict = {'epoch': self.currentEpoch }
            for m in self.metrics:
                s = re.findall(r' - '+m+': ([-+]?\d*\.\d+|\d+)', line)
                if len(s)>0:
                    mDict[m] = float(s[-1])
            self.task.push('output.training_history', mDict)
        if(randint(0,9)>5):
            updateDict['status.info'] = line[:150]
            self.task.update(updateDict)
        return True
    except Exception as e:
        print('failed to parse output')
        traceback.print_exc()
        return False

class KerasProcess(ProcessTaskProcessor):
    metrics = ['loss', 'val_loss']
    currentEpoch = -1
    totalEpoch = 0
    def process_output(self, line):
        return parseTrainingProgress(self,line)


class ProgressTracker(keras.callbacks.Callback):
    def __init__(self, task):
        self.task = task
        self.start_time = time.time()
        super(ProgressTracker, self).__init__()
        self.task.set('status.progress', 0)

    def on_batch_begin(self, batch, logs={}):
        if self.task.abort.is_set():
            self.task.set('status.error', 'interrupted')
            self.model.stop_training = True
            raise Exception('interrupted')

    def on_batch_end(self, batch, logs={}):
        info = ''
        for k, v in logs.items():
            if isinstance(v, (np.ndarray, np.generic) ):
                vstr = str(v.tolist())
            else:
                vstr = str(v)
            info += "{}: {}\n".format(k,vstr)
        self.elapsed_time = time.time()-self.start_time
        info += "elapsed_time: {:.2f}s".format(self.elapsed_time)
        self.task.update({
            'status.info': info,
            'status.progress': batch%100
        })

    def on_epoch_begin(self, epoch, logs={}):
        self.task.set('status.stage', 'epoch #'+str(epoch))
        if hasattr(self.model.optimizer, 'lr'):
            if self.task.get('config.learning_rate'):
                lr = float(self.task.get('config.learning_rate'))
                K.set_value(self.model.optimizer.lr, lr)
        else:
            self.task.set('status.error', 'Optimizer must have a "lr" attribute.')

    def on_epoch_end(self, epoch, logs={}):
        report = {}
        report['epoch'] = epoch
        for k, v in logs.items():
            report[k] = v
        if hasattr(self.model.optimizer, 'lr'):
            report['lr'] = K.get_value(self.model.optimizer.lr).tolist()
        self.task.push('output.training_history', report)
        self.task.set('output.elapsed_time', "%.2fs"%self.elapsed_time)
        self.task.set('output.last_epoch_update_time', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
