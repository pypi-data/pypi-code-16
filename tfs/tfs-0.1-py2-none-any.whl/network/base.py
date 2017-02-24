import tensorflow as tf
import numpy as np
from tfs.core.layer import func_table
from tfs.core.util import run_once_for_each_obj
import new

def _layer_function(layerclass):
  def func(self,*args,**kwargs):
    layer = layerclass(*args,**kwargs)
    layer._net = self
    self.layers.append(layer)
    return self
  return func

def _network_meta(future_class_name, future_class_parents, future_class_attr):
  for k in func_table:
    future_class_attr[k]=_layer_function(func_table[k])
  return type(future_class_name, future_class_parents, future_class_attr)

# decorators
def with_graph(f):
  def with_graph_run(self,*args,**kwargs):
    with self.graph.as_default():
      return f(self,*args,**kwargs)
  # this is important to make the decorator compatiable with run_once_each_obj.
  with_graph_run.__name__=f.__name__
  return with_graph_run


class Network(object):
  __metaclass__ = _network_meta
  def __init__(self):
    self.layers=[]
    self._in = None
    self._out = None
    self._graph = tf.Graph()
    with self.graph.as_default():
      self._sess = tf.Session()
    self.setup()

  def __del__(self):
    self.sess.close()

  def setup(self):
    '''Construct the network. '''
    raise NotImplementedError('Must be implemented by the subclass.')

  @property
  def graph(self):
    return self._graph

  @property
  def sess(self):
    return self._sess

  @with_graph
  @run_once_for_each_obj
  def build(self,input_shape,dtype=tf.float32):
    """Build the computational graph
    inTensor: the network input tensor.
    """
    self._in = tf.placeholder(dtype,input_shape)
    tmp = self._in
    for l in self.layers:
      tmp = l.build(tmp)
    self._out = tmp
    return tmp

  def run(self,eval_list,feed_dict):
    return self.sess.run(eval_list, feed_dict=feed_dict)

  @with_graph
  def initialize(self):
    return self.sess.run(tf.global_variables_initializer())

  @with_graph
  def load(self, data_path, ignore_missing=False):
    '''Load network weights.
    data_path: The path to the numpy-serialized network weights
    session: The current TensorFlow session
    ignore_missing: If true, serialized weights for missing layers are ignored.
    '''
    data_dict = np.load(data_path).item()
    for op_name in data_dict:
      with tf.variable_scope(op_name, reuse=True):
        for param_name, data in data_dict[op_name].iteritems():
          try:
            var = tf.get_variable(param_name)
            self.sess.run(var.assign(data))
          except ValueError:
            if not ignore_missing:
              raise

  def copy(self):
    obj = NetworkCopy()
    for l in self.layers:
      obj.layers.append(l.copyTo(obj))
    if hasattr(self,'_has_run') and Network.build.__name__ in self._has_run:
      input_shape = self._in.get_shape().as_list()
      obj.build(input_shape)
    return obj

class NetworkCopy(Network):
  """this classes is used for initialize a network object for methods such as
'copy' and 'subnet'

  """
  def setup(self):
    """We don't need to set up when we construct a NetworkCopy Instance
    """
    pass
