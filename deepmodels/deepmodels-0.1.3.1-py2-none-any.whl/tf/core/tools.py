"""Tools for tensorflow deepmodels.
"""

from deepmodels.tf.core.commons import DataType, DataFileType


def gen_data_filename(fn_prefix,
                      file_type=DataFileType.METADATA,
                      data_type=DataType.TRAIN):
  """Generate filename for corresponding data.

  Args:
    fn_prefix: prefix of the filename.
    file_type: target file type.
    data_type: type of data file.
  Returns:
    generated filename.
  """
  if file_type == DataFileType.METADATA:
    if data_type == DataType.TRAIN:
      return "{}__train.csv".format(fn_prefix)
    if data_type == DataType.TEST:
      return "{}__test.csv".format(fn_prefix)
    if data_type == DataType.LABEL:
      return "{}__labels.txt".format(fn_prefix)
  if file_type == DataFileType.TFRECORD:
    if data_type == DataType.TRAIN:
      return "{}__train.tfrecord".format(fn_prefix)
    if data_type == DataType.TEST:
      return "{}__test.tfrecord".format(fn_prefix)
    if data_type == DataType.VALIDATE:
      return "{}__validate.tfrecord".format(fn_prefix)


def convert_data_filename(input_fn, dst_file_type, dst_data_type):
  """Convert one data filename to another.

  Args:
    input_fn: input data filename.
    There should be no '__' in filename other than the last part.
    dst_file_type: target data file type.
    dst_data_type: target data type.
  Returns:
    converted data filename.
  """
  sep_idx = input_fn.find("__")
  assert sep_idx != -1, "invalid input data filename."
  return gen_data_filename(input_fn[:sep_idx], dst_file_type, dst_data_type)
