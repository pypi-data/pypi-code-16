"""Complete sample of training and finetuning a dataset using DeepModels.

The dataset is organized as folders of categories.
"""

import numpy as np
import os
import cPickle as pickle

from tqdm import tqdm

from sklearn import tree
from sklearn import linear_model
from sklearn import svm
from sklearn import metrics
from sklearn.model_selection import train_test_split

import tensorflow as tf
import tensorflow.contrib.slim as slim

from deepmodels.tf.core import commons
from deepmodels.tf.core import common_flags
from deepmodels.tf.core import base_model
from deepmodels.tf.core import model_zoo
from deepmodels.tf.core.learners import dm_classifier
from deepmodels.tf.core.dm_models import dm_model_factory
from deepmodels.tf.data import img_folder_data
from deepmodels.tf.models import net_downloader_tf

tf.logging.set_verbosity(tf.logging.INFO)

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_string("data_dir", "", "directory containing image data")
flags.DEFINE_string("data_name", "test", "dataset name.")
flags.DEFINE_integer("opt", 0, "optimization method.")


class FinetuneModel(model_zoo.NetworkDM):
  """Network model for finetuning.

  We use Inceptionv4 as base model, but it can be easily changed to others.
  """
  incep4_model = dm_model_factory.get_dm_model(commons.ModelType.INCEPTION_V4)

  def __init__(self):
    self.net_params = commons.ModelParams(
        "finetune_model",
        commons.ModelType.CUSTOM,
        input_img_height=self.incep4_model.net_params.input_img_height,
        input_img_width=self.incep4_model.net_params.input_img_width)

  def build_model(self, inputs, learner_type=commons.LearnerType.Classifier):
    _, endpoints = self.incep4_model.build_model(inputs)
    # get feature output.
    basenet_output = endpoints[self.incep4_model.net_params.output_layer_name]
    if len(basenet_output.get_shape()) > 2:
      basenet_output_flat = slim.flatten(
          basenet_output, scope="baseoutput_flatten")
    else:
      basenet_output_flat = basenet_output
    # add ft layer.
    new_logits = slim.fully_connected(
        basenet_output_flat,
        self.net_params.cls_num,
        activation_fn=None,
        scope="ft/logits")
    # monitor ft layer output.
    base_model.add_tensor_summary(
        new_logits.name, new_logits, use_histogram=True, use_sparsity=True)
    return new_logits, endpoints

  def get_preprocess_fn(self):
    self.incep4_model.net_params.model_mode = commons.ModelMode.TEST
    return self.incep4_model.get_preprocess_fn()


class NewModel(model_zoo.NetworkDM):
  """Network model for training from stratch.
  """
  pass


class TFLinearClf(dm_classifier.DMClassifier):
  """A one layer linear classifier for tensorflow.
  """

  def build_model(self, inputs, model_params):
    with tf.variable_scope("ft"):
      logits = slim.fully_connected(
          inputs, model_params.cls_num, activation_fn=None, scope="logits")
      self.input_tensor_name = inputs.name
      self.output_tensor_name = logits.name
      return logits, None


def train_new_clf():
  """Train a classifier from stratch.
  """
  # create model.
  # prepare data.
  pass


def train_ft_clf():
  """Train finetune classifier.
  """
  # create model.
  my_model = FinetuneModel()

  # prepare data.
  my_data = img_folder_data.ImgFolderData(FLAGS.data_name, FLAGS.data_dir,
                                          commons.ImgFormat.JPG)
  img_batch, label_batch, samp_num, cls_num = my_data.get_data_for_clf(
      commons.DataType.TRAIN,
      batch_size=FLAGS.batch_size,
      target_img_height=my_model.net_params.input_img_height,
      target_img_width=my_model.net_params.input_img_width,
      preprocess_fn=my_model.get_preprocess_fn())
  print("[train_ft_clf] we have {} samples of {} classes.".format(samp_num, cls_num))
  my_model.net_params.cls_num = cls_num

  # train model.
  my_clf = dm_classifier.DMClassifier()
  my_clf.set_dm_model(my_model)
  _opt_method = commons.OPTMethod.SGD
  if FLAGS.opt == 1:
    _opt_method = commons.OPTMethod.MOMENTUM
  if FLAGS.opt == 2:
    _opt_method = commons.OPTMethod.ADAM
  if FLAGS.opt == 3:
    _opt_method = commons.OPTMethod.ADAGRAD
  if FLAGS.opt == 4:
    _opt_method = commons.OPTMethod.RMSPROP
  train_params = commons.TrainTestParams(
      FLAGS.log_dir,
      samp_num,
      FLAGS.batch_size,
      init_learning_rate=FLAGS.lrate,
      max_epochs=FLAGS.epochs,
      opt_method=_opt_method,
      use_regularization=False)
  train_params.fine_tune = True
  train_params.custom["model_fn"] = my_model.incep4_model.net_weight_fn
  if not os.path.exists(train_params.custom["model_fn"]):
    net_downloader_tf.download_net(commons.ModelTypes.INCEPTION_V4)
  # decay learning rate every 5 epochs.
  train_params.decay_steps = train_params.batch_num_per_epoch * 5
  # only train last layer.
  train_params.train_scopes = ["ft/logits"]
  # restore whole model except added layer.
  train_params.restore_scopes_exclude = ["ft"]
  train_params.resume_training = FLAGS.resume_training
  # adaptive gpu memory usage.
  config = tf.ConfigProto()
  config.gpu_options.allow_growth = True
  train_params.session_config = config
  my_clf.train(img_batch, label_batch, None, train_params)


def eval_clf():
  """Evaluate a trained classifier.
  """
  # set model.
  my_model = FinetuneModel()
  # get data.
  my_data = img_folder_data.ImgFolderData(FLAGS.data_name, FLAGS.data_dir,
                                          commons.ImgFormat.JPG)
  img_batch, label_batch, samp_num, cls_num = my_data.get_data_for_clf(
      commons.DataType.TEST,
      batch_size=FLAGS.batch_size,
      target_img_height=my_model.net_params.input_img_height,
      target_img_width=my_model.net_params.input_img_width,
      preprocess_fn=my_model.get_preprocess_fn())
  # set model.
  my_model.net_params.cls_num = cls_num
  my_clf = dm_classifier.DMClassifier()
  my_clf.set_dm_model(my_model)
  test_params = commons.TrainTestParams(FLAGS.log_dir, samp_num,
                                        FLAGS.batch_size)
  my_clf.test(img_batch, label_batch, None, test_params)


def train_clf_on_feats():
  """Train a classifier on deep features.
  """
  my_data = img_folder_data.ImgFolderData(FLAGS.data_name, FLAGS.data_dir,
                                          commons.ImgFormat.JPG)
  feat_fn = os.path.join(FLAGS.data_dir,
                         "{}_feats.pkl".format(my_data.dataset_name_))
  if not os.path.exists(feat_fn):
    incep4_model = dm_model_factory.get_dm_model(
        commons.ModelType.INCEPTION_V4)
    incep4_model.net_params.model_mode = commons.ModelMode.TEST
    img_batch, label_batch, samp_num, cls_num = my_data.get_data_for_clf(
        commons.DataType.TEST,
        batch_size=FLAGS.batch_size,
        target_img_height=incep4_model.net_params.input_img_height,
        target_img_width=incep4_model.net_params.input_img_width,
        preprocess_fn=incep4_model.get_preprocess_fn())
    # set model.
    incep_clf = dm_classifier.DMClassifier()
    incep_clf.set_dm_model(incep4_model)
    _, endpoints = incep_clf.build_model(img_batch, None)
    incep4_model.net_params.output_layer_name = endpoints[
        "PreLogitsFlatten"].name
    incep_clf.load_model_from_checkpoint_fn(incep4_model.net_weight_fn)
    # extract features.
    batches_per_epoch = int(samp_num / FLAGS.batch_size)
    all_feats = None
    all_labels = None
    print "extracting features..."
    try:
      with incep_clf.sess.as_default():
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)
        for _ in tqdm(range(batches_per_epoch)):
          cur_imgs, cur_labels = incep_clf.sess.run([img_batch, label_batch])
          cur_feats = incep_clf.get_output(
              cur_imgs, incep4_model.net_params.output_layer_name)
          if all_feats is None:
            all_feats = cur_feats
          else:
            all_feats = np.vstack((all_feats, cur_feats))
          if all_labels is None:
            all_labels = cur_labels
          else:
            all_labels = np.vstack((all_labels, cur_labels))
        coord.request_stop()
        coord.join(threads)
    except Exception as ex:
      print str(ex)
    print "features extracted."

    # save to file.
    with open(feat_fn, "wb") as f:
      data = {"feats": all_feats, "labels": all_labels}
      pickle.dump(data, f)
      print "feature data saved."

  # load data.
  with open(feat_fn, "rb") as f:
    data = pickle.load(f)
    all_feats = data["feats"]
    all_labels = data["labels"]
    cls_num = len(np.unique(all_labels))
    print "feature data loaded."
    print "cls num: {}".format(cls_num)
    print "total sample number: {}".format(len(all_feats))
  train_feats, test_feats, train_labels, test_labels = train_test_split(
      all_feats, all_labels, test_size=0.2, random_state=42)
  # train a classifier.
  clf1 = tree.DecisionTreeClassifier()
  clf1.fit(train_feats, train_labels)
  pred_labels = clf1.predict(test_feats)
  score = metrics.accuracy_score(test_labels, pred_labels)
  print "decision tree classifier score: {}".format(score)

  clf2 = linear_model.LogisticRegression()
  clf2.fit(train_feats, train_labels)
  pred_labels2 = clf2.predict(test_feats)
  score2 = metrics.accuracy_score(test_labels, pred_labels2)
  print "logistic classifier score: {}".format(score2)
  clf_fn = os.path.join(FLAGS.data_dir, "logistic_clf.pkl")
  with open(clf_fn, "wb") as f:
    pickle.dump(clf2, f)
    print "classifier saved to file."
  with open(clf_fn, "rb") as f:
    clf2 = pickle.load(f)
    print "classifier loaded from file."
    pred_labels2 = clf2.predict(test_feats)
    score2 = metrics.accuracy_score(test_labels, pred_labels2)
    print "restored logistic classifier score: {}".format(score2)

  clf3 = svm.SVC()
  clf3.fit(train_feats, train_labels)
  pred_labels3 = clf3.predict(test_feats)
  score3 = metrics.accuracy_score(test_labels, pred_labels3)
  print "svm score: {}".format(score3)

  return

  # train tf linear classifier; similar as finetuning the last layer.
  model_params = commons.ModelParams(
      "ft", commons.ModelType.CUSTOM, cls_num=cls_num)
  clf4 = TFLinearClf()
  to_train = True
  if to_train:
    feat_tensor = tf.convert_to_tensor(train_feats, dtype=tf.float32)
    label_tensor = tf.convert_to_tensor(train_labels, dtype=tf.int64)
    feat, label = tf.train.slice_input_producer(
        [feat_tensor, label_tensor], shuffle=True, seed=161803)
    feat_batch, label_batch = tf.train.shuffle_batch(
        [feat, label],
        batch_size=FLAGS.batch_size,
        capacity=FLAGS.batch_size * 50,
        min_after_dequeue=FLAGS.batch_size * 20)
    samp_num = len(train_feats)
    train_params = commons.TrainTestParams(
        FLAGS.log_dir,
        samp_num,
        FLAGS.batch_size,
        init_learning_rate=FLAGS.lrate,
        max_epochs=FLAGS.epochs,
        opt_method=commons.OPTMethod.MOMENTUM,
        use_regularization=False)
    clf4.train(feat_batch, label_batch, model_params, train_params)

  # evaluate
  inputs = tf.placeholder(dtype=tf.float32, shape=(None, test_feats.shape[1]))
  logits, _ = clf4.build_model(inputs, model_params)
  ckpt = os.path.join(FLAGS.log_dir, "train", "model.ckpt-3600")
  clf4.load_model_from_checkpoint_fn(ckpt)
  pred_labels4 = clf4.get_output(train_feats, logits.name)
  pred_labels4 = np.argmax(pred_labels4, axis=1)
  score4 = metrics.accuracy_score(test_labels, pred_labels4)
  print "tf classifier score: {}".format(score4)


def main(_):
  if FLAGS.task == 0:
    train_ft_clf()
  if FLAGS.task == 1:
    eval_clf()
  if FLAGS.task == 2:
    train_clf_on_feats()
  if FLAGS.task == 3:
    my_data = img_folder_data.ImgFolderData(FLAGS.data_name, FLAGS.data_dir,
                                            commons.ImgFormat.JPG)
    my_data.create_base_data()


if __name__ == "__main__":
  tf.app.run()
