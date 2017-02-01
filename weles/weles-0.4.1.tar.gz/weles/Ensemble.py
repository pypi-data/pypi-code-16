from abc import ABCMeta, abstractmethod
from Algorithm import *
import numpy as np
import random

# To ensure deterministic loop we use randomization with fixed seed.
SEED = 123
random.seed(SEED)

class Ensemble(Algorithm):
    __metaclass__ = ABCMeta
    def __init__(self, dataset):
        # we're gathering the dataset
        self.dataset = dataset

    @abstractmethod
    def predict():
        pass

    @abstractmethod
    def learn():
        pass
