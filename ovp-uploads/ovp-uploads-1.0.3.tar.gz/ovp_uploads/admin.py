from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _

from ovp_uploads.models import UploadedImage


class UploadedImageAdmin(admin.ModelAdmin):
  fields = [
  	'id', 'image', 'image_small', 'image_medium', 'image_large'
  ]

  list_display = [
  	'id', 'image', 'user'
  ]

  list_filter = []

  list_editable = []

  search_fields = [
  	'id', 'user__name', 'user__email'
  ]

  readonly_fields = [
  	'id', 'image_small', 'image_medium', 'image_large'
  ]

  raw_id_fields = [
  	'user'
  ]


admin.site.register(UploadedImage, UploadedImageAdmin)


