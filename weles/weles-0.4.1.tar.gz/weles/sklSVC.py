# Adapter for sklearn
from Dataset import *
from Classifier import *
from sklAdapter import *

from sklearn import svm

class sklSVC(sklAdapter):
    def __init__(self, dataset, configuration):
        Classifier.__init__(self,dataset)
        self.clf = svm.SVC()
