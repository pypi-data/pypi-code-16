from abc import ABCMeta, abstractmethod
import numpy as np

class Algorithm:
    __metaclass__ = ABCMeta
    def quickLoop(self):
        folds = xrange(0,5,1)
        acc = []
        bac = []
        for fold in folds:
            self.dataset.setCV(fold)
            self.learn()
            self.dataset.clearSupports()
            self.predict()
            scores = self.dataset.score()
            acc.append(scores['accuracy'])
            bac.append(scores['bac'])
        acc = np.mean(acc)
        bac = np.mean(bac)
        return {'acc': acc, 'bac': bac}
