"""Object view image visualizer.

Draw views in an html to look at and debug.
"""

import csv
import math

import tensorflow as tf

from ..core import commons
import data_manager

flags = tf.app.flags
FLAGS = flags.FLAGS

flags.DEFINE_string("input", "", "input metadata file.")
flags.DEFINE_string("output", "", "output data file.")


def vis_img_meta(metadata_fn, save_fn, show_percent=0.5):
  """Visualize image files from a metadata file to an html file.

  Args:
    metadata_fn: metadata file.
    save_fn: html file to save.
    show_percent: percentage of samples to show. 
  """
  label_fn = data_manager.convert_data_filename(metadata_fn,
                                                commons.DataFileType.DATA_LABEL)
  with open(label_fn, "r") as fin:
    labels = fin.readlines()
    labels = [x.rstrip() for x in labels]
  with open(metadata_fn, "r") as fin:
    num_rows = len(fin.readlines())
    print "csv row number: {}".format(num_rows)
    fin.seek(0)
    records = csv.reader(fin)
    with open(save_fn, "w") as fout:
      html_str = "<html><body>"
      cnt = 0
      for row in records:
        cnt += 1
        if cnt > num_rows * show_percent:
          break
        img_fn = row[0]
        img_label = int(row[1])
        label_name = labels[img_label]
        cur_div = """
<div>
  <img src=\"{}\"><br>
  <h3>{}</h3>
</div>        
"""
        cur_div = cur_div.format(img_fn, label_name)
        html_str += cur_div
      html_str += "</body></html>"
      fout.write(html_str)
      print "data saved to {}".format(save_fn)


def vis_view_pair(metadata_fn, save_fn):
  """Produce an html page with view pair images.

  Args:
    metadata_fn: csv metadata file containing view pair info.
    save_fn: file path to save the html page.
  """
  with open(metadata_fn, "r") as fin:
    records = csv.reader(fin)
    with open(save_fn, "w") as fout:
      html_str = "<html><body>"
      for row in records:
        view1_fn = row[0]
        view2_fn = row[1]
        obj_label = row[2]
        pose_x = float(row[3])
        pose_y = float(row[4])
        pose_z = float(row[5])
        pose_x_deg = pose_x * 180 / math.pi
        pose_y_deg = pose_y * 180 / math.pi
        pose_z_deg = pose_z * 180 / math.pi
        cur_div = """
<div>
  <img src=\"{}__depth.png\"> <img src=\"{}__depth.png\">
  <h3>Same object: {}</h3>
  <h3>relative pose (radius): {}, {}, {}</h3>
  <h3>relative pose (degree): {}, {}, {}</h3>
</div>
"""
        cur_div = cur_div.format(view1_fn, view2_fn, obj_label,
                                 pose_x, pose_y, pose_z,
                                 pose_x_deg, pose_y_deg, pose_z_deg)
        html_str += cur_div
      html_str += "</body></html>"
      fout.write(html_str)
      print "data saved to {}".format(save_fn)


def main(_):
  vis_img_meta(FLAGS.input, FLAGS.output)
  # vis_view_pair(FLAGS.input, FLAGS.output)


if __name__ == "__main__":
  tf.app.run()
