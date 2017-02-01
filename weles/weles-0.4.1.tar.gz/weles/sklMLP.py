# Adapter for sklearn
from Dataset import *
from Classifier import *
from sklAdapter import *

from sklearn import neural_network

class sklMLP(sklAdapter):
    def __init__(self, dataset, configuration):
        Classifier.__init__(self,dataset)
        self.clf = neural_network.MLPClassifier(
            solver='lbfgs',
            alpha=1e-5,
            hidden_layer_sizes=(5, 2),
            random_state=1)
