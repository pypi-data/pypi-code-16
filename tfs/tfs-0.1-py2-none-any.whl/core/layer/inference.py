import tensorflow as tf
import numpy as np
import ops
from base import Layer

class Softmax(Layer):
  def __init__(self,
               name=None
  ):
    Layer.__init__(
      self,
      name
    )
  def build(self,inTensor):
    self._in = inTensor
    with tf.variable_scope(self.name) as scope:
      output = tf.nn.softmax(inTensor,name=self.name)
    self._out = output
    return output



