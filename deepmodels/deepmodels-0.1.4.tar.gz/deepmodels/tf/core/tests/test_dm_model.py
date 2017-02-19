"""Test dm models.
"""

import tensorflow as tf

from deepmodels.tf.core import commons
from deepmodels.tf.core.dm_models import dm_vgg, dm_inception, dm_cifar


class DMModelTest(tf.test.TestCase):
  def test_vgg16(self):
    vgg16 = dm_vgg.VGGDM(commons.ModelType.VGG16)
    self.assertIsNotNone(vgg16.get_label_names())
    self.assertIsNotNone(vgg16.get_preprocess_fn())
    with self.assertRaises(ValueError) as context:
      dm_vgg.VGGDM(commons.ModelType.INCEPTION_V1)

  def test_vgg19(self):
    vgg19 = dm_vgg.VGGDM(commons.ModelType.VGG19)
    self.assertIsNotNone(vgg19.get_label_names())
    self.assertIsNotNone(vgg19.get_preprocess_fn())

  def test_incep(self):
    incep4 = dm_inception.InceptionDM(commons.ModelType.INCEPTION_V4)
    print incep4.net_weight_fn

  def test_cifar(self):
    cifar10 = dm_cifar.CIFARDM(commons.ModelType.CIFAR10)
    print cifar10.get_label_names()


if __name__ == "__main__":
  tf.test.main()
