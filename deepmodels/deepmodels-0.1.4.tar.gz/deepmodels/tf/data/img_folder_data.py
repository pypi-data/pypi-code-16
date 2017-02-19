"""Generic data manager for images organized by folders.

Each folder is a category.
"""

import os

from deepmodels.tf.core import commons
from deepmodels.tf.core import data_provider
from deepmodels.tf.core import tools

from deepmodels.tf.data import dm_data


class ImgFolderData(dm_data.DMData):
  """Class to manage image dataset organized by category folders.
  """
  root_dir_ = ""
  img_format_ = commons.ImgFormat.JPG
  dataset_name_ = "test"
  save_fn_prefix_ = ""
  train_meta_fn = ""
  test_meta_fn = ""
  label_fn = ""
  train_record_fn = ""
  test_record_fn = ""

  def __init__(self, dataset_name, root_dir, img_format=commons.ImgFormat.JPG):
    """Init parameters.

    Args:
      dataset_name: name of the dataset. Used to create files.
      root_dir: root folder of image files.
      img_format: jpg or png.
    """
    self.root_dir_ = root_dir
    self.img_format_ = img_format
    self.dataset_name_ = dataset_name
    self.save_fn_prefix_ = os.path.join(self.root_dir_, self.dataset_name_)
    self.train_meta_fn = tools.gen_data_filename(self.save_fn_prefix_,
                                                 commons.DataFileType.METADATA,
                                                 commons.DataType.TRAIN)
    self.test_meta_fn = tools.gen_data_filename(self.save_fn_prefix_,
                                                commons.DataFileType.METADATA,
                                                commons.DataType.TEST)
    self.label_fn = tools.gen_data_filename(self.save_fn_prefix_,
                                            commons.DataFileType.METADATA,
                                            commons.DataType.LABEL)
    self.train_record_fn = tools.gen_data_filename(
        self.save_fn_prefix_, commons.DataFileType.TFRECORD,
        commons.DataType.TRAIN)
    self.test_record_fn = tools.gen_data_filename(
        self.save_fn_prefix_, commons.DataFileType.TFRECORD,
        commons.DataType.TEST)

  def gen_metadata(self):
    """Generate metadata files from image folders.
    """
    if not os.path.exists(self.train_meta_fn) and not os.path.exists(
        self.test_meta_fn):
      data_provider.gen_clf_metadata_from_img_fns(self.root_dir_,
                                                  self.save_fn_prefix_)

  def gen_tfrecord_data(self):
    """Create tfrecord data from metadata files.

    This will create additional files, but it's more compact
    and easier to transfer to server for training.
    """
    if not os.path.exists(self.train_record_fn):
      data_provider.convert_clf_data_to_tfrecord(self.train_meta_fn,
                                                 self.train_record_fn)
    if not os.path.exists(self.test_record_fn):
      data_provider.convert_clf_data_to_tfrecord(self.test_meta_fn,
                                                 self.test_record_fn)

  def create_base_data(self):
    """Create basic data.
    """
    self.gen_metadata()
    self.gen_tfrecord_data()

  def get_data_for_clf(self,
                       data_type=commons.DataType.TRAIN,
                       batch_size=32,
                       target_img_height=299,
                       target_img_width=299,
                       preprocess_fn=None):
    """A thin wrapper on top of data_provider function.

    Args:
      data_type: type of data to load.
      batch_size: size of batch.
      target_img_width: image width.
      target_img_height: image height.
      preprocess_fn: function for preprocessing.
    """
    if not os.path.exists(self.train_record_fn):
      self.create_base_data()

    if data_type == commons.DataType.TRAIN:
      data_fn = self.train_record_fn
    if data_type == commons.DataType.TEST:
      data_fn = self.test_record_fn
    all_data = data_provider.input_clf_data_from_tfrecord(
        data_fn,
        self.label_fn,
        img_format=self.img_format_,
        img_depth=3,
        img_width=target_img_width,
        img_height=target_img_height,
        batch_size=batch_size,
        preprocess_fn=preprocess_fn,
        shuffle=True)
    img_batch, label_batch, samp_num, cls_num = all_data
    print "loaded data. sample number: {}; class number: {}".format(samp_num,
                                                                    cls_num)
    return img_batch, label_batch, samp_num, cls_num
