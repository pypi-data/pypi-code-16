# Adapter for sklearn
from Dataset import *
from Classifier import *
from sklAdapter import *

class sklAdapter(Classifier):
    __metaclass__ = ABCMeta
    # === Learning ===
    def learn(self):
        self.clf.fit(self.dataset.X, self.dataset.y)
        pass

    def predict(self):
        predictions = self.clf.predict(self.dataset.testX)
        for idx, val in enumerate(predictions):
            self.dataset.test[idx].prediction = val
