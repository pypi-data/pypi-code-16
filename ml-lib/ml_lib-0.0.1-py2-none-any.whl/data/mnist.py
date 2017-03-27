from data import Data
from tensorflow.examples.tutorials.mnist import input_data
import numpy as np

class MNIST(Data):
    def __init__(self, inputs_per_batch=50, flat=True):
        mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
        self.train_inputs = mnist.train.images
        self.train_labels = mnist.train.labels
        self.test_inputs = mnist.test.images
        self.test_labels = mnist.test.labels
        self.flat = flat
        if not self.flat:
            self.train_inputs = np.reshape(self.train_inputs, [-1, 28, 28, 1])
            self.test_inputs = np.reshape(self.test_inputs, [-1, 28, 28, 1])
        self.inputs_dim = self.train_inputs[0].shape
        self.labels_dim = self.train_labels[0].shape
        self.inputs_per_batch = inputs_per_batch

    def get_train_data_iterator(self):
        for i in range(0, self.train_inputs.shape[0], self.inputs_per_batch):
            yield self.train_inputs[i:i+self.inputs_per_batch], self.train_labels[i:i+self.inputs_per_batch]

    def get_test_data_iterator(self):
        for i in range(0, self.test_inputs.shape[0], self.inputs_per_batch):
            yield self.test_inputs[i:i+self.inputs_per_batch], self.test_labels[i:i+self.inputs_per_batch]