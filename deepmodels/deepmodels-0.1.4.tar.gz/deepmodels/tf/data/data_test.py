"""Tester for public datasets.
"""

import tensorflow as tf

import mnist_data
import cifar_data


def test_mnist():
  """Perform tasks with mnist data.
  """
  mnist = mnist_data.MNISTData()
  mnist.download()


def test_cifar():
  cifar10 = cifar_data.CIFAR10Data()
  cifar10.download()


if __name__ == "__main__":
  test_mnist()