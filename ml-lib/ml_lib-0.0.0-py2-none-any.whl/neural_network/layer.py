import tensorflow as tf

class Layer(object):
    def __init__(self, name):
        self.name = name

    def get_output(self, i, i_dim, o_dim):
        raise notImplementedError()
    
    def get_name(self):
        return self.name

class ConvLayer(Layer):
    def __init__(self, name='conv_layer', activation_f=tf.nn.relu, filter_dim=[4, 4]):
        super(ConvLayer, self).__init__(name=name)
        self.activation_f = activation_f
        self.filter_dim = filter_dim

    def get_output(self, i, i_dim, o_dim):
        assert len(i_dim) == len(o_dim) == 3
        assert list(i_dim[:2]) == [item*2 for item in o_dim[:2]]
        w_dim = self.filter_dim + [i_dim[-1], o_dim[-1]]
        b_dim = [o_dim[-1], ]
        w = tf.Variable(tf.random_normal(w_dim), name='w')
        b = tf.Variable(tf.random_normal(b_dim), name='b')
        o = tf.nn.conv2d(i, w, strides=[1, 1, 1, 1], padding='SAME') + b
        o = self.activation_f(o)
        o = tf.nn.max_pool(o, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
        return o

class FlatteningLayer(Layer):
    def __init__(self, name='flattening_layer', activation_f=tf.nn.relu):
        super(FlatteningLayer, self).__init__(name=name)
        self.activation_f = activation_f

    def get_output(self, i, i_dim, o_dim):
        assert len(o_dim) == 1
        i_flattened_dim = reduce((lambda x, y: x * y), i_dim)
        w_dim = [i_flattened_dim, o_dim[0]]
        b_dim = o_dim
        w = tf.Variable(tf.random_normal(w_dim), name='w')
        b = tf.Variable(tf.random_normal(b_dim), name='b')
        o = tf.reshape(i, [-1, i_flattened_dim])
        o = self.activation_f(tf.matmul(o, w) + b)
        return o

class FullyConnectedLayer(Layer):
    def __init__(self, name='fully_connected_layer', activation_f=tf.nn.relu):
        super(FullyConnectedLayer, self).__init__(name=name)
        self.activation_f = activation_f

    def get_output(self, i, i_dim, o_dim):
        assert len(i_dim) == len(o_dim) == 1
        w = tf.Variable(tf.random_normal([i_dim[0], o_dim[0]]), name='w')
        b = tf.Variable(tf.random_normal(o_dim), name='b')
        o = self.activation_f(tf.matmul(i, w) + b)
        return o