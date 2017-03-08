"""Demonstrate how to work with tfrecords.
"""

import numpy as np

import tensorflow as tf


def EncodeImage(image_tensor):
  """Convert an image tensor to encoded string.
  """
  with tf.Session():
    image_encoded = tf.image.encode_png(tf.constant(image_tensor)).eval()
  return image_encoded


def Read(record_file):
  """Read data from tfrecord file.
  """
  keys_to_features = {
      'view1/image/encoded': tf.FixedLenFeature(
          (), dtype=tf.string, default_value=''),
      'view1/image/format': tf.FixedLenFeature(
          [], dtype=tf.string, default_value='png'),
      'view1/image/height': tf.FixedLenFeature(
          [1], dtype=tf.int64, default_value=64),
      'view1/image/width': tf.FixedLenFeature(
          [1], dtype=tf.int64, default_value=64),
      'view2/image/encoded': tf.FixedLenFeature(
          (), dtype=tf.string, default_value=''),
      'view2/image/format': tf.FixedLenFeature(
          [], dtype=tf.string, default_value='png'),
      'view2/image/height': tf.FixedLenFeature(
          [1], dtype=tf.int64, default_value=64),
      'view2/image/width': tf.FixedLenFeature(
          [1], dtype=tf.int64, default_value=64),
      'image/encoded': tf.FixedLenFeature(
          [2], dtype=tf.string, default_value=['', '']),
      'same_object': tf.FixedLenFeature(
          [1], dtype=tf.int64, default_value=-1),
      'relative_pos': tf.FixedLenFeature(
          [3], dtype=tf.float32),
  }
  with tf.Graph().as_default():
    filename_queue = tf.train.string_input_producer([record_file], capacity=10)
    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(filename_queue)
    example = tf.parse_single_example(serialized_example, keys_to_features)
    #png1 = example['view1/image/encoded']
    #png2 = example['view2/image/encoded']
    png = example['image/encoded']
    coord = tf.train.Coordinator()
    print 'Reading images:'
    with tf.Session() as sess:
      queue_threads = tf.train.start_queue_runners(sess=sess, coord=coord)
      #image1, image2 = sess.run([png1, png2])
      image1, image2 = sess.run([png[0], png[1]])
      # print "example read: {}, {}".format(image1.shape, image2.shape)
    coord.request_stop()
    coord.join(queue_threads)


def write_tfrecord(save_fn):
  """Generate sample images to test encoding.
  """
  image_tensor1 = np.random.randint(255, size=(4, 5, 3)).astype(np.uint8)
  image_tensor2 = np.random.randint(255, size=(4, 5, 3)).astype(np.uint8)
  print "input imgs: {}, {}".format(image_tensor1.shape, image_tensor2.shape)
  png1 = EncodeImage(image_tensor1)
  png2 = EncodeImage(image_tensor2)
  # Note: for the png files, just use png1 = f1.read()
  # basic feature type: byte, float, int64.
  example = tf.train.Example(features=tf.train.Features(feature={
      'view1/image/encoded':
      tf.train.Feature(bytes_list=tf.train.BytesList(value=[png1])),
      'view1/image/height':
      tf.train.Feature(int64_list=tf.train.Int64List(value=[4])),
      'view1/image/width':
      tf.train.Feature(int64_list=tf.train.Int64List(value=[5])),
      'view1/image/format':
      tf.train.Feature(bytes_list=tf.train.BytesList(value=['png'])),
      'view2/image/encoded':
      tf.train.Feature(bytes_list=tf.train.BytesList(value=[png2])),
      'view2/image/height':
      tf.train.Feature(int64_list=tf.train.Int64List(value=[4])),
      'view2/image/width':
      tf.train.Feature(int64_list=tf.train.Int64List(value=[5])),
      'view2/image/format':
      tf.train.Feature(bytes_list=tf.train.BytesList(value=['png'])),
      'image/encoded':
      tf.train.Feature(bytes_list=tf.train.BytesList(value=[png1, png2])),
      'same_object':
      tf.train.Feature(int64_list=tf.train.Int64List(value=[1])),
      'relative_pos':
      tf.train.Feature(float_list=tf.train.FloatList(value=[1.2, 0.4, -0.9]))
  }))
  # write examples.
  examples = [example]
  with tf.python_io.TFRecordWriter(save_fn) as writer:
    for record in examples:
      record_str = record.SerializeToString()
      writer.write(record_str)


def main(_):
  tfrecord_fn = "/Users/jiefeng/dev/data/tf_test/dm_test.tfrecord"
  write_tfrecord(tfrecord_fn)
  Read(tfrecord_fn)


if __name__ == "__main__":
  tf.app.run()
