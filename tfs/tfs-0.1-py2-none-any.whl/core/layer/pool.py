import tensorflow as tf
import numpy as np
import ops
from base import Layer

class MaxPool(Layer):
  def __init__(self,
               ksize,
               strides,
               padding='SAME',
               name=None
  ):
    Layer.__init__(
      self,
      ksize,
      strides,
      padding,
      name
    )
  def build(self,inTensor):
    self._in = inTensor
    kx,ky = self.param.ksize
    sx,sy = self.param.strides
    with tf.variable_scope(self.name) as scope:
      output = tf.nn.max_pool(inTensor,
                              ksize=[1,kx,ky,1],
                              strides=[1,sx,sy,1],
                              padding=self.param.padding,
                              name=self.name)
    self._out = output
    return output

  def inverse(self,outTensor):
    self._inv_in = outTensor
    name = 'inv_'+self.name
    outshape = self._out.get_shape().as_list()
    outshape[0]=-1 # the first dimension is used for batch
    if outTensor.get_shape().ndims != 4:
      outTensor = tf.reshape(outTensor,outshape)
    print outTensor.get_shape()
    out = ops.max_unpool(outTensor,self._out,name)
    print 'inv_max_pool ' + str(outTensor.get_shape().as_list()) + '->' + str(out.get_shape().as_list())
    self._inv_out = out
    return out


class AvgPool(Layer):
  def __init__(self,
               ksize,
               strides,
               padding='SAME',
               name=None
  ):
    Layer.__init__(
      self,
      ksize,
      strides,
      padding,
      name
    )
  def build(self,inTensor):
    self._in = inTensor
    kx,ky = self.param.ksize
    sx,sy = self.param.strides
    with tf.variable_scope(self.name) as scope:
      output = tf.nn.avg_pool(inTensor,
                              ksize=[1,kx,ky,1],
                              strides=[1,sx,sy,1],
                              padding=self.param.padding,
                              name=self.name)
    self._out = output
    return output
