# Adapter for sklearn
from Dataset import *
from Classifier import *
from sklAdapter import *

from sklearn import neighbors

class sklKNN(sklAdapter):
    def __init__(self, dataset, configuration):
        Classifier.__init__(self,dataset)
        self.k = configuration['k']
        self.clf = neighbors.KNeighborsClassifier(self.k)
