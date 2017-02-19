"""Download pretrained TensorFlow model weights.
"""

import os
import sys
import tarfile

from six.moves import urllib

from deepmodels.tf.core import commons
from deepmodels.tf.core.dm_models import dm_model_factory

net_weight_urls = {
    commons.ModelType.INCEPTION_V2:
    "https://www.dropbox.com/s/yb70rjnwevp3zvu/inception_v2_2016_08_28.tar.gz?dl=1",
    commons.ModelType.INCEPTION_V3:
    "https://www.dropbox.com/s/x0yhlu1nabol899/inception_v3_2016_08_28.tar.gz?dl=1",
    commons.ModelType.INCEPTION_V4:
    "https://www.dropbox.com/s/aroz5rg2c0u69cs/inception_v4_2016_09_09.tar.gz?dl=1",
    commons.ModelType.VGG16:
    "https://www.dropbox.com/s/op3rj7jef22vsn8/vgg_16_2016_08_28.tar.gz?dl=1",
    commons.ModelType.VGG19:
    "https://www.dropbox.com/s/qibqbkjiklmn6a2/vgg_19_2016_08_28.tar.gz?dl=1"
}


def download_net(net_type):
  """Download net data from private dropbox (jiefeng).

  Args:
    net_type: type of network.
  """
  net = dm_model_factory.get_dm_model(net_type)
  # create folder for net.
  cur_dir = os.path.dirname(os.path.realpath(__file__))
  net_dir = os.path.join(cur_dir, net.net_params.model_name)
  print "network model directory: {}".format(net_dir)
  if not os.path.exists(net_dir):
    os.mkdir(net_dir)
  weight_fn = net_weight_urls[net_type].split("/")[-1].split("?")[0]
  weight_path = os.path.join(net_dir, weight_fn)

  # download model weights file.
  def _progress(count, block_size, total_size):
    sys.stdout.write("\r>> Downloading {} {:03}".format(
        weight_fn, float(count * block_size) / float(total_size) * 100.0))
    sys.stdout.flush()

  filepath, _ = urllib.request.urlretrieve(net_weight_urls[net_type],
                                           weight_path, _progress)
  print()
  statinfo = os.stat(filepath)
  print("Successfully downloaded", weight_fn, statinfo.st_size, "bytes.")
  # unzip file.
  tarfile.open(filepath, 'r:gz').extractall(net_dir)
  print "tar unzipped."
  # remove downloaded file.
  os.remove(filepath)
  print "{} removed.".format(filepath)


if __name__ == "__main__":
  download_net(commons.ModelType.INCEPTION_V4)
