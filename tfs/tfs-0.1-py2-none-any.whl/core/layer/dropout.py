import tensorflow as tf
import numpy as np
import ops
from base import Layer

class Dropout(Layer):
  def __init__(self,
               keep_prob,
               name=None
  ):
    Layer.__init__(
      self,
      keep_prob,
      name
    )
  def build(self,inTensor):
    self._in = inTensor
    output = tf.nn.dropout(inTensor, self.param.keep_prob,
                           name=self.param.name)
    self._out = output
    return output

