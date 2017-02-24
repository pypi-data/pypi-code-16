from base import FileLists,DataSubset
import numpy as np
import os

def unpickle(file):
  import cPickle
  fo = open(file, 'rb')
  dict = cPickle.load(fo)
  fo.close()
  return dict



class Dataset(object):
  width=32
  height=32
  channels=3
  def __init__(self,data_dir):
    self.train = self.load([os.path.join(data_dir, 'data_batch_%d' % i)
                            for i in xrange(1, 6)])
    self.test = self.load([os.path.join(data_dir,'test_batch')])

  def load(self,filenames):
    data = []
    labels = []
    for f in FileLists(filenames):
      batch=unpickle(f)
      data.append(batch['data'])
      labels.append(batch['labels'])
    data = np.concatenate(data)
    labels = np.concatenate(labels)
    data = data.reshape([-1,self.width,self.height,self.channels])
    return DataSubset(data,labels)

