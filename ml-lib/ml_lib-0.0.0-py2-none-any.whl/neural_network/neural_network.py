import tensorflow as tf

class NeuralNetwork(object):
    def __init__(self, data, layers, layers_dims, cost_f, accuracy_f, gradient_f, prediction_f,
                 iteration_period=1000, save_period=1):
        self.data = data
        self.layers = layers
        self.layers_dims = layers_dims
        self.cost_f = cost_f
        self.accuracy_f = accuracy_f
        self.gradient_f = gradient_f
        self.prediction_f = prediction_f
        self.iteration_period = iteration_period
        self.save_period = save_period

    def make_computation_graph(self):
        with tf.name_scope('inputs') as scope:
            inputs_dim = list(self.data.get_inputs_dim())
            inputs_dim.insert(0, None)
            self.x = tf.placeholder(tf.float32, shape=inputs_dim)
            tf.add_to_collection('x', self.x)

        with tf.name_scope('labels') as scope:
            outputs_dim = list(self.data.get_labels_dim())
            outputs_dim.insert(0, None)
            self.y_hat = tf.placeholder(tf.float32, shape=outputs_dim)

        n_layers = len(self.layers_dims)
        layers_outputs = [self.x]
        for i in range(n_layers):
            with tf.name_scope(self.layers[i].get_name()) as scope:
                if i == 0:
                    layer_input_dim = inputs_dim[1:]
                else:
                    layer_input_dim = self.layers_dims[i-1]
                output = self.layers[i].get_output(layers_outputs[-1], layer_input_dim, self.layers_dims[i])
                layers_outputs.append(output)
        self.y = layers_outputs[-1]

        with tf.name_scope('cost_function') as scope:
            self.cost = self.cost_f(self.y, self.y_hat)

        with tf.name_scope('gradient_function') as scope:
            self.train_step = self.gradient_f(self.cost)

        with tf.name_scope('accuracy_function') as scope:
            self.accuracy = self.accuracy_f(self.y, self.y_hat)

        with tf.name_scope('prediction_function') as scope:
            self.prediction = self.prediction_f(self.y)
            tf.add_to_collection('prediction', self.prediction)

        self.list = tf.placeholder(tf.float32)
        self.mean = tf.reduce_mean(self.list)
        tf.summary.scalar('test_accuracy', self.mean)
        self.merged_summaries = tf.summary.merge_all()

    def get_training_iterator(self, restore_point=None):
        saver = tf.train.Saver()
        sess = tf.Session()
        if restore_point is None:
            sess.run(tf.global_variables_initializer())
        else:
            saver.restore(sess, restore_point)
            print("restored checkpoint \"%s\"" % (restore_point))
        writer = tf.summary.FileWriter('logs', sess.graph)
        i = 0
        epoch = 0
        data_iterator = self.data.get_train_data_iterator()
        while True:
            try:
                input_batch, label_batch = next(data_iterator)
            except StopIteration:
                data_iterator = self.data.get_train_data_iterator()
                input_batch, label_batch = next(data_iterator)
                epoch += 1
                if epoch % self.save_period == 0:
                    print("starting epoch %d, saving model..." % (epoch))
                    saver.save(sess, 'logs/backup', global_step=epoch)
                    print("model saved, computing test accuracy...")
                    test_data_iterator = self.data.get_test_data_iterator()
                    test_accuracy = [] # list that holds the test accuracy for each batch
                    while True:
                        try:
                            test_input_batch, test_label_batch = next(test_data_iterator)
                            test_accuracy.append(
                                sess.run(self.accuracy, feed_dict={self.x: test_input_batch,
                                                                   self.y_hat: test_label_batch})
                            )
                        except StopIteration:
                            break
                    print("test accuracy: %g" % sess.run(self.mean, feed_dict={self.list: test_accuracy}))
                    summary = sess.run(self.merged_summaries, feed_dict={self.list: test_accuracy})
                    writer.add_summary(summary, epoch)

            sess.run(self.train_step, feed_dict={self.x: input_batch, self.y_hat: label_batch})
            if i % self.iteration_period == 0:
                train_accuracy = sess.run(self.accuracy, feed_dict={self.x: input_batch, self.y_hat: label_batch})
                print("training accuracy at step %d: %g" % (i, train_accuracy))
                yield train_accuracy
            i += 1