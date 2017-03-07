""" Basic Feed Forward Neural Network Implementation """
import numpy as np
import matplotlib.pyplot as plt


# Miscellaneous Functions
def sigmoid(z):
    """ The sigmoid function """
    return 1.0/(1.0 + np.exp(-z))


def sigmoid_prime(z):
    """ first derivative of the sigmoid function """
    return sigmoid(z) * (1 - sigmoid(z))


def output_activation(z):
    """ output layer activation function """
    pass


class NN(object):
    def __init__(self, sizes):
        """ INPUTS
                sizes:
                a list of the size of each layer of the network
                ex: [2, 3, 1] would be a 3 layer network with the first layer consisting of 2 neurons,
                the second with 3, and the 3rd with 1. Weights and biases are initialized randomly with a Gaussian
                with mean 0 and variance 1. The first layer is an input layer, and therefore has no biases. """
        np.random.seed(0)
        self.num_layers = len(sizes)
        self.sizes = sizes
        # list of biases for each layer. each element i is an array of size n, where n is the # of neurons in layer i
        self.biases = [np.random.randn(1, y) for y in sizes[1:]] # bias list of column vectors doesnt include 1st layer
        # initialize a weight list to store the weights connecting neurons between adjacent layers
        # each element of the weight list is a numpy array with y rows and x columns
        # each element (i, j) of the array is the weight from neuron i in layer L to neuron j in layer L+1
        # Example:
        #      A    B
        # ----------------
        # X | 0.1  0.2      Layer L + 1 contains 2 neurons (A and B). Layer L contains 3 neurons (X, Y, and Z).
        # Y | 0.3  0.4      Their associated weights are stores in the matrix shown.
        # Z | 0.5  0.6
        #
        self.weights = [np.random.randn(x, y) for x, y in zip(sizes[:-1], sizes[1:])]

    def feedforward(self, a):
        """ return the output of the network if vector `a` is input """
        if a.size != self.sizes[0]:
            print 'Error: Input Size Does Not Match Input Layer Size'
            return
        # perform h(x) = sigmoid(w*a + b) for each layer
        for b, w in zip(self.biases, self.weights):
            # perform the dot product of the activations from the previous layer and the weights to this layer
            # and reshape it so we have a proper vector to add to b
            dot = np.reshape(np.dot(a, w), b.shape)
            a = sigmoid(dot + b)
        return a

    def SGD(self, epochs, eta, x, y, plot_errors):
        """ Train the network using Stochastic Gradient Descent

        epochs: max number of training epochs
        x: training set
        y: training labels
        eta: learning rate
        plot_errors: whether or not to generate an error plot after training is complete

        """

        errors = []
        for i in range(epochs):
            prnt = True if (i % 100) == 0 else False
            if prnt:
                print '************************************************'
                print 'Training Epoch ', i
            err = self.backprop(x, y, eta, prnt)
            errors.append(err)

        if plot_errors:
            plt.plot(range(len(errors)), errors, 'bo')
            plt.title('Training Error')
            plt.xlabel('Epochs')
            plt.ylabel('|Error|')
            plt.grid()
            plt.show()

    def backprop(self, x, y, eta, print_outputs):
        """ The backpropagation algorithm for training

         x: training set
         y: training set labels
         eta: learning rate
         print_outputs: whether or not to print outputs

         """

        # storing the activations, layer by layer
        activations = [x]

        # forward pass
        # perform h(x) = sigmoid(w*a + b) for each layer
        a = x
        for b, w in zip(self.biases, self.weights):
            # perform the dot product of the activations from the previous layer and the weights to this layer
            # and reshape it so we have a proper vector to add to b
            dot = np.reshape(np.dot(a, w), b.shape)
            a = sigmoid(dot + b)
            activations.append(a)

        output_layer = activations[-1]
        layer_error = (y - output_layer).T
        # multiply output from previous layer by the output layer errors to get the output layer weight updates
        output_delta = np.multiply(layer_error, activations[-2])
        # use the learning rate and update the weights at the output layer
        update = eta * output_delta
        self.weights[-1] += update.T

        # loop through the hidden layers back to the input layer and backpropagate
        for i in range(1, self.num_layers - 1):
            weights = self.weights[-i]  # the weights connecting layer L to layer L + 1
            layer_error = np.dot(weights, layer_error)  # error in layer L propagated from layer L + 1
            ins = activations[-(i+2)]  # input from layer L - 1
            update = eta * layer_error * ins  # update for the weights is the activation from L-1 times error in L
            self.weights[-(i+1)] += update.T

        if print_outputs:
            print 'OUTPUT: ', output_layer
            print 'TARGET: ', y

        return sum(layer_error)

    def train(self, epochs, X, Y, eta, gen_plots):
        """ Method used for training the neural net by a user

        epochs: max number of epochs to run
        X: training set
        Y: training set labels
        eta: learning rate
        gen_plots: (boolean) generate training error plots for each training example

        """
        for (sample, label) in zip(X, Y):
            self.SGD(epochs, eta, sample, label, gen_plots)
