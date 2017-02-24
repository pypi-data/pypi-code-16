from tfs.core.util import *
import tensorflow as tf
class DeconvVisNet(object):
  def __init__(self,netobj,nsamples=1):
    with netobj.graph.as_default():
      self.net = netobj
      netobj._nsamples = nsamples
      inv_in_shape = netobj._out.get_shape().as_list()
      self._inv_in = netobj._out
      tmp = self._inv_in
      for l in netobj.layers[::-1]:
        tmp = l.inverse(tmp)
      self._inv_out = tmp
      layers = {}
      for l in netobj.layers:
        layers[l.name]=l._out
      self.layers= layers

  def vis_image(self,layer_name,channel_id,image):
    layer_output = self.net.sess.run(
      self.layers[layer_name],
      feed_dict={
        self.net._in:image
      })
    to_vis=np.zeros_like(layer_output)
    to_vis[0,...,channel_id]=layer_output[0,...,channel_id]

    generated = self.net.sess.run(
      self._inv_out,
      feed_dict={
        self.layers[layer_name]:to_vis,
        self.net._in:image
      })
    gen_img=ensure_uint255(norm01c(generated[0,:],0))
    return gen_img[:,:,::-1]


