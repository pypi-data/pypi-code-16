import tensorflow as tf
import numpy as np
import ops
from base import Layer

class LRN(Layer):
  def __init__(self,
               radius,
               alpha,
               beta,
               bias=1.0,
               name=None
  ):
    Layer.__init__(
      self,
      radius,
      alpha,
      beta,
      bias,
      name
    )
  def build(self,inTensor):
    self._in = inTensor
    with tf.variable_scope(self.name) as scope:
      output = tf.nn.local_response_normalization(inTensor,
                                                  depth_radius=self.param.radius,
                                                  alpha=self.param.alpha,
                                                  beta=self.param.beta,
                                                  bias=self.param.bias,
                                                  name=self.name)
    self._out = output
    return output

class BN(Layer):
  def __init__(self,
               scale_offset=True,
               activation=ops.relu,
               name=None
  ):
    Layer.__init__(
      self,
      scale_offset,
      activation,
      name
    )
  def build(self,inTensor):
    self._in = inTensor
    input_shape = inTensor.get_shape()
    shape = [input_shape[-1]]
    with tf.variable_scope(self.name) as scope:
      if scale_offset:
        scale = tf.get_variable('scale', shape=shape)
        offset = tf.get_variable('offset', shape=shape)
      else:
        scale, offset = (None, None)
      output = tf.nn.batch_normalization(
        inTensor,
        mean=tf.get_variable('mean', shape=shape),
        variance=tf.get_variable('variance', shape=shape),
        offset=offset,
        scale=scale,
        # TODO: This is the default Caffe batch norm eps
        # Get the actual eps from parameters
        variance_epsilon=1e-5,
        name=self.name)
      if self.param.activation:
        output = self.param.activation(output)
    self.variables={
      'scale':scale,
      'offset':offset,
      'mean':mean,
      'variance':variance,
    }
    self._out = output
    return output

