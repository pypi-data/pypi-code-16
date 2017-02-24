import tensorflow as tf
import numpy as np
import ops
from base import Layer

class FullyConnect(Layer):
  def __init__(self,
               outdim,
               activation = ops.relu,
               name=None
  ):
    Layer.__init__(
      self,
      outdim,
      activation,
      name
    )

  def build(self,inTensor):
    self._in = inTensor
    input_shape = inTensor.get_shape()
    with tf.variable_scope(self.name) as scope:
      if input_shape.ndims == 4:
        # The input is spatial. Vectorize it first.
        dim = np.prod(input_shape.as_list()[1:])
        output = tf.reshape(inTensor, [-1,dim])
      else:
        output, dim = (inTensor, input_shape[-1].value)
      weights = tf.get_variable('weights', shape=[dim, self.param.outdim])
      biases = tf.get_variable('biases', [self.param.outdim])
      output = tf.nn.xw_plus_b(output, weights, biases,name=scope.name)
      if self.param.activation:
        output= self.param.activation(output, name=scope.name)
    self.variables={
      'weights':weights,
      'biases':biases,
    }
    self._out = output
    return output

  def inverse(self,outTensor):
    self._inv_in = outTensor
    name = 'inv_'+self.name
    act = self.param.activation
    with tf.variable_scope(name) as scope:
      if act:
        outTensor = act(outTensor)
      weights = tf.transpose(self.variables['weights'])
      inv_fc = tf.matmul(outTensor,weights)
      print 'inv_fc '+str(outTensor.get_shape().as_list()) + '->' + str(inv_fc.get_shape().as_list())
      self._inv_out = inv_fc
      return inv_fc

