"""Sample of loading a trained model to do prediction.
"""

import time
import numpy as np

import tensorflow as tf
import tensorflow.contrib.slim as slim

from deepmodels.tf.core import commons
from deepmodels.tf.core import common_flags
from deepmodels.tf.core import data_provider
from deepmodels.tf.core.dm_models import dm_model_factory
from deepmodels.tf.core.learners.dm_classifier import DMClassifier

flags = tf.app.flags
FLAGS = flags.FLAGS


def classify_imgs(img_format=commons.ImgFormat.JPG,
                  net_type=commons.ModelType.VGG16):
  """Perform classification on images of a given directory.

  Args:
    img_format: format of image files.
    net_type: type of pretrained model.
  """
  dm_model = dm_model_factory.get_dm_model(net_type)
  dm_model.net_params.model_mode = commons.ModelMode.TEST
  preprocess_fn = dm_model.get_preprocess_fn()
  if FLAGS.img_dir != "":
    imgs, img_fns = data_provider.load_img_fns(
        FLAGS.img_dir,
        dm_model.net_params.input_img_width,
        dm_model.net_params.input_img_height,
        img_format=img_format,
        preprocess_fn=preprocess_fn)
    assert len(img_fns) > 0, "no image files found."
  if FLAGS.input_meta != "":
    batch_data = data_provider.clf_input_from_image_fns(
        FLAGS.input_meta,
        3,
        dm_model.net_params.input_img_width,
        dm_model.net_params.input_img_height,
        FLAGS.batch_size,
        scaling=True,
        preprocess_fn=preprocess_fn,
        shuffle=True)
    imgs, _, fn_batch, _, _ = batch_data
    img_fns = fn_batch.eval(session=tf.Session())

  # build model.
  my_clf = DMClassifier()
  my_clf.set_dm_model(dm_model)
  my_clf.build_model(imgs, None)
  model_fn = dm_model.net_weight_fn
  my_clf.load_model_from_checkpoint_fn(model_fn)
  all_imgs = imgs.eval(session=tf.Session())
  # prediction.
  print "start prediction..."
  startt = time.time()
  pred_labels, pred_probs = my_clf.predict(all_imgs)
  print "prediction done. {}s / img".format(
      (time.time() - startt) / len(all_imgs))
  top_k = 5
  label_to_name = dm_model.net_label_names
  for img_id in range(len(img_fns)):
    fn_parts = img_fns[img_id].split("/")
    disp_fn = "{}/{}".format(fn_parts[-2], fn_parts[-1])
    print "image: {}".format(disp_fn)
    for k in range(top_k):
      cur_label = pred_labels[img_id, k]
      cur_prob = pred_probs[img_id, k]
      print "{}:{} ({})".format(k, label_to_name[cur_label], cur_prob)
    print ""


# TODO(jiefeng): finish implementation.
def classify_imgs_from_pb(img_dir, img_format=commons.ImgFormat.JPG):
  """Use model saved in pb file, e.g. inceptionv3 production version.
  """
  pass
  # load data.
  # net_params = model_zoo.net_params[commons.NetNames.INCEPTION_V3]
  # imgs, img_fns = data_provider.load_img_fns(
  #     img_dir,
  #     net_params.input_img_width,
  #     net_params.input_img_height,
  #     img_format=img_format)


def main(_):
  tf.logging.set_verbosity(tf.logging.INFO)
  classify_imgs(
      img_format=commons.ImgFormat.PNG,
      net_type=commons.ModelType.INCEPTION_V4)


if __name__ == "__main__":
  tf.app.run()
