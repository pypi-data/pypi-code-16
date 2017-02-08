import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.deconstruct import deconstructible

from django_resized import ResizedImageField

@deconstructible
class ImageName(object):
  def __init__(self, sub_path=""):
      self.path = sub_path

  def __call__(self, instance, filename):
      ext = filename.split('.')[-1]
      filename = "%s.%s" % (instance.uuid, ext)
      return 'user-uploaded/images%s/%s' % (self.path, filename)

image = ImageName()
image_small = ImageName("-small")
image_medium = ImageName("-medium")
image_large = ImageName("-large")

class UploadedImage(models.Model):
  def save(self, *args, **kwargs):
    if not self.pk:
      self.uuid = str(uuid.uuid4())
    # If _committed == False, it means the image is not uploaded to s3 yet
    # (will be uploaded on super.save()). This means the image is being updated
    # So we update other images accordingly
    if not self.image._committed:
      self.image_small = self.image._file # ._file because we need the InMemoryUploadedFile instance
      self.image_medium = self.image._file
      self.image_large = self.image._file

    self.modified_date = timezone.now()

    return super(UploadedImage, self).save(*args, **kwargs)

  def __str__(self):
    return self.uuid

  class Meta:
    app_label = 'ovp_uploads'
    verbose_name = _('uploaded image')
    verbose_name_plural = _('uploaded images')

  user = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, null=True, blank=True)
  image = models.ImageField(_('Image 350x260'), upload_to=image)
  image_small = ResizedImageField(size=[350, 260], upload_to=image_small, blank=True, null=True, default=None)
  image_medium = ResizedImageField(size=[420, 312], upload_to=image_medium, blank=True, null=True, default=None)
  image_large = ResizedImageField(size=[1260, 936], upload_to=image_large, blank=True, null=True, default=None)
  created_date = models.DateTimeField(auto_now_add=True)
  modified_date = models.DateTimeField(auto_now=True)
  uuid = models.CharField('UUID', max_length=36, default=None, null=False, blank=True)

