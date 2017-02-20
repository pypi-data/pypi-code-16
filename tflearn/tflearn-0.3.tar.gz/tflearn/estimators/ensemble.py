from __future__ import division, print_function, absolute_import

import os
import time
from datetime import datetime
import numpy as np

import tensorflow as tf
from tensorflow.contrib.tensor_forest.python import tensor_forest
from tensorflow.contrib.tensor_forest.python.ops import data_ops
from tensorflow.python.ops import state_ops, array_ops, math_ops
import tensorflow.contrib.framework as fw

from ..data_flow import ArrayFlow


class RandomForest:
    """ Random Forest.

    Args:
        num_classes: `int`. Total number of class. In case of a regression, set to 1
            and set regression=True.
        num_features: Total number of features.
        num_trees: `int`, Number of Trees.
        max_nodes: `int`, Number of Nodes.
        split_after_samples: `int`. Split after the given samples.
        metric: `func` returning a `Tensor`. The metric function.
        graph: `tf.Graph`. The model TensorFlow Graph. If None, one will be
            created.
        session: `tf.Session`. A TensorFlow Session for running the graph.
            If None, one will be created.
        log_dir: `str`. The path to save tensorboard logs.
        max_checkpoints: int`. Maximum number of checkpoints to keep. Older
            checkpoints will get replaced by newer ones. Default: Unlimited.
        global_step: `Tensor`. A TensorFlow Variable for counting steps.
            If None, one will be created.
        regression: `bool`. Set to 'True' in case of a regression task.
        name: `str`. The model name.

    """

    def __init__(self, num_classes, num_features, num_trees=100, max_nodes=1000,
                 split_after_samples=25, metric=None, graph=None, session=None,
                 log_dir='/tmp/snaplearn/ckpt', max_checkpoints=5,
                 global_step=None,
                 regression=False, name='RandomForest'):

        self.graph = graph or tf.Graph()  # tf.get_default_graph()
        self.metric = metric
        self.log_dir = log_dir
        self.max_ckpt = max_checkpoints
        self._pred = None
        self._input_pred = None
        self._to_be_restored = False
        self._not_initialized = True
        self.name = name
        # set contrib params
        self.num_features = num_features
        self.num_classes = num_classes
        with self.graph.as_default():
            self.global_step = global_step
            self.session = session or tf.Session()
            self.params = tensor_forest.ForestHParams(
                num_classes=num_classes, num_features=num_features,
                num_trees=num_trees,
                max_nodes=max_nodes, split_after_samples=split_after_samples,
                regression=regression).fill()
            self.graph_builder = tensor_forest.RandomForestGraphs(self.params)

    def fit(self, X, Y, n_steps=10000, batch_size=512, display_step=100,
            snapshot_step=1000):
        """ fit.

        Train model.

        Args:
            Args:
            X: `Tensor` or `Tensor list`. The input data. It must be a list of
                `Tensor` in case of multiple inputs.
            Y: `Tensor`. The labels/targets tensor.
            n_steps: `int`. Total number of steps to run the training.
            batch_size: `int`. The batch size.
            display_step: `int`. The step to display information on screen.
            snapshot_step: `int`. The step to snapshot the model (save and
                evaluate if valX/valY provided).
            n_epoch: Maximum number of epich (Unlimited by default).

        """

        with self.graph.as_default():
            if isinstance(X, tf.Tensor) and isinstance(Y, tf.Tensor):
                if len(Y.get_shape().as_list()) > 1:
                    raise Exception("Labels must be 1-D tensor.")
                # Optional Image and Label Batching
                X, Y = tf.train.shuffle_batch([X, Y], batch_size=batch_size,
                                              min_after_dequeue=batch_size,
                                              capacity=batch_size * 4,
                                              num_threads=1)

            # Array Input
            elif X is not None and Y is not None:
                if len(list(np.shape(Y))) > 1:
                    raise Exception("Labels must be 1-D array.")
                # Create a queue using feed_dicts
                cr = ArrayFlow(X, Y, batch_size, shuffle=True)
                X, Y = cr.get()
                X = tf.reshape(X, [-1, self.num_features])
                Y = tf.reshape(Y, [-1, 1])

            X, _, spec = data_ops.ParseDataTensorOrDict(X)
            Y2 = data_ops.ParseLabelTensorOrDict(Y)

            if self.global_step is None:
                self.global_step = fw.get_or_create_global_step()

            train_op = tf.group(self.graph_builder.training_graph(X, Y2),
                                state_ops.assign_add(self.global_step, 1))
            loss_op = self.graph_builder.training_loss(X, Y)

            self._init_graph()

            # start TensorFlow QueueRunner's
            tf.train.start_queue_runners(sess=self.session)
            if cr:
                cr.launch_threads(self.session)

            gstep = self.global_step.eval(session=self.session)

            for step in range(1, n_steps + 1):

                start_time = time.time()
                if (step) % display_step == 0:
                    _, loss_val = self.session.run(
                        [train_op, loss_op])  # TODO: Add acc
                else:
                    _, loss_val = self.session.run([train_op, loss_op])
                duration = time.time() - start_time

                if (step) % display_step == 0:
                    examples_per_sec = batch_size / duration
                    sec_per_batch = duration
                    if self.metric:
                        format_str = '%s: step %d, loss = %.2f, acc = %.2f, ' \
                                     '(%.1f examples/sec; %.3f sec/batch)'
                        print(format_str % (
                        datetime.now(), step + gstep, loss_val,
                        examples_per_sec, sec_per_batch))
                    else:
                        format_str = '%s: step %d, loss = %.2f, ' \
                                     '(%.1f examples/sec; %.3f sec/batch)'
                        print(format_str % (
                        datetime.now(), step + gstep, loss_val,
                        examples_per_sec, sec_per_batch))

                if (step) % snapshot_step == 0 and step != 0:
                    self.saver.save(self.session, self.log_dir,
                                    global_step=self.global_step)

    def _init_graph(self):
        # Initialize all weights
        if self._not_initialized:
            self.saver = tf.train.Saver()
            self.session.run(tf.global_variables_initializer())
            self._not_initialized = False
        # Restore weights if needed
        if self._to_be_restored:
            self.saver = tf.train.Saver()
            self.saver.restore(self.session, self._to_be_restored)
            self._to_be_restored = False

    def _build_pred_graph(self):
        with self.graph.as_default():
            # Creates data placeholder
            self._input_pred = tf.placeholder(tf.float32,
                                              shape=[None,
                                                     self.params.num_features],
                                              name='pred_input')
            p, _, spec = data_ops.ParseDataTensorOrDict(self._input_pred)
            self._pred = self.graph_builder.inference_graph(p)
            self._init_graph()

    def predict(self, X):
        """ predict.

        Predict scores of the given batch array.

        Args:
            X: `Array` or `list` of `Array`. The array to predict.

        Return:
            `Array` or `list` of `Array`. Prediction scores result.

        """
        # First call build prediction network
        if self._pred is None or self._to_be_restored:
            self._build_pred_graph()
        return self.session.run(self._pred, feed_dict={self._input_pred: X})

    def evaluate(self, X, Y, metric=None, batch_size=1000):
        """ evaluate.

        Evaluate model performance given data and metric.

        Args:
            X: `Tensor` or `Tensor list`. The input data. It must be a list of
                `Tensor` in case of multiple inputs.
            Y: `Tensor`. The labels/targets tensor.
            metric: `func` returning a `Tensor`. The metric function.
            batch_size: `int`. The batch size.

        Return:
            The metric value.

        """

        with self.graph.as_default():
            if metric is None:
                if self.metric is None:
                    raise Exception("No metric provided!")
                else:
                    metric = self.metric

            if isinstance(X, tf.Tensor) and isinstance(Y, tf.Tensor):
                total_samples = X.get_shape().as_list()[0]
                # Optional Image and Label Batching
                X, Y = tf.train.shuffle_batch([X, Y], batch_size=batch_size,
                                              min_after_dequeue=batch_size,
                                              capacity=batch_size * 4,
                                              num_threads=1)

            # Array Input
            elif X is not None and Y is not None:
                total_samples = len(X)
                # Create a queue using feed_dicts
                cr = ArrayReader(X, Y, batch_size, shuffle=False)
                X, Y = cr.get_data()
                X = tf.reshape(X, [-1, self.num_features])
                Y = tf.reshape(Y, [-1, 1])

            X, _, spec = data_ops.ParseDataTensorOrDict(X)
            Y = data_ops.ParseLabelTensorOrDict(Y)

            n_batches = int(total_samples / batch_size)

            pred = self.graph_builder.inference_graph(X)

            if not self.params.regression:
                Y = math_ops.to_int64(array_ops.one_hot(math_ops.to_int64(
                    array_ops.squeeze(Y)), self.params.num_classes, 1, 0))
                Y = tf.reshape(Y, [-1, self.num_classes])

            metric_op = metric(pred, Y)

            self._init_graph()

            tf.train.start_queue_runners(sess=self.session)
            if cr:
                cr.start_threads(self.session)

            m = 0
            for i in range(n_batches):
                m += self.session.run(metric_op) / n_batches

            return m

    def save(self, path):
        """ save.

        Save model to the given path.

        Args:
            path: `str`. The path to save the model.

        """
        self.saver.save(self.session, os.path.abspath(path))

    def load(self, path):
        """ load.

        Restore model from the given path.

        Args:
            path: `str`. The model path.

        """
        with self.graph.as_default():
            self.session = tf.Session()
            self._not_initialized = True
            self._to_be_restored = os.path.abspath(path)
