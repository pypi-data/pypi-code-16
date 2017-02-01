# Adapter for sklearn
from Dataset import *
from Classifier import *
from sklAdapter import *

from sklearn import naive_bayes

class sklGNB(sklAdapter):
    def __init__(self, dataset, configuration):
        Classifier.__init__(self,dataset)
        self.clf = naive_bayes.GaussianNB()
