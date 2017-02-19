"""Common flags for tasks.
"""

import tensorflow as tf

from deepmodels.tf.core import commons

# turn on logging by default.
tf.logging.set_verbosity(tf.logging.INFO)

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_string("log_dir", "", "Directory to save train and test log.")
flags.DEFINE_integer("mode", 0, "0: train mode; 1: test mode.")
flags.DEFINE_integer("img_format", commons.ImgFormat.PNG, "png or jpg.")
flags.DEFINE_string("img_dir", "", "image directory.")
flags.DEFINE_string("save_prefix", "", "prefix for saved meta files.")
flags.DEFINE_float("train_ratio", 0.8,
                   "ratio between training and testing data.")
flags.DEFINE_integer("batch_size", 32, "batch size of input data.")
flags.DEFINE_float("lrate", 0.01, "learning rate.")
flags.DEFINE_integer("epochs", 10, "number of epochs")
flags.DEFINE_integer("resume_training", 0, "0: restart; 1: resume")

flags.DEFINE_string("input_meta", "", "input meta data file.")
flags.DEFINE_integer("task", 0, "0: train; 1: test")
flags.DEFINE_float("test_ratio", 1, "how much test samples to run.")
