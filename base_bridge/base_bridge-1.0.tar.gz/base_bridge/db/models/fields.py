# coding=utf-8

from django.db import models as raw_models

__author__ = 'Maple.Liu'


class AutoField(raw_models.AutoField):
    def __init__(self, *args, **kwargs):
        super(AutoField, self).__init__(*args, **kwargs)


class BigIntegerField(raw_models.BigIntegerField):
    def __init__(self, *args, **kwargs):
        super(BigIntegerField, self).__init__(*args, **kwargs)


class BinaryField(raw_models.BinaryField):
    def __init__(self, *args, **kwargs):
        super(BinaryField, self).__init__(*args, **kwargs)


class BooleanField(raw_models.BooleanField):
    def __init__(self, *args, **kwargs):
        kwargs['default'] = False
        super(BooleanField, self).__init__(*args, **kwargs)


class CharField(raw_models.CharField):
    def __init__(self, max_length=1024, *args, **kwargs):
        kwargs['max_length'] = max_length
        super(CharField, self).__init__(*args, **kwargs)


class CommaSeparatedIntegerField(raw_models.CommaSeparatedIntegerField):
    def __init__(self, *args, **kwargs):
        super(CommaSeparatedIntegerField, self).__init__(*args, **kwargs)


class DateField(raw_models.DateField):
    def __init__(self, *args, **kwargs):
        super(DateField, self).__init__(*args, **kwargs)


class DateTimeField(raw_models.DateTimeField):
    def __init__(self, *args, **kwargs):
        super(DateTimeField, self).__init__(*args, **kwargs)


class DecimalField(raw_models.DecimalField):
    def __init__(self, *args, **kwargs):
        super(DecimalField, self).__init__(*args, **kwargs)


class EmailField(raw_models.EmailField):
    def __init__(self, *args, **kwargs):
        super(EmailField, self).__init__(*args, **kwargs)


class FileField(raw_models.FileField):
    def __init__(self, *args, **kwargs):
        super(FileField, self).__init__(*args, **kwargs)


class FilePathField(raw_models.FilePathField):
    def __init__(self, *args, **kwargs):
        super(FilePathField, *args, **kwargs)


class FloatField(raw_models.FloatField):
    def __init__(self, *args, **kwargs):
        super(FloatField, self).__init__(*args, **kwargs)


class ImageField(raw_models.ImageField):
    def __init__(self, *args, **kwargs):
        super(ImageField, self).__init__(*args, **kwargs)


class IntegerField(raw_models.IntegerField):
    def __init__(self, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)


class IPAddressField(raw_models.IPAddressField):
    def __init__(self, *args, **kwargs):
        super(IPAddressField, self).__init__(*args, **kwargs)


class GenericIPAddressField(raw_models.GenericIPAddressField):
    def __init__(self, *args, **kwargs):
        super(GenericIPAddressField, self).__init__(*args, **kwargs)


class NullBooleanField(raw_models.NullBooleanField):
    def __init__(self, *args, **kwargs):
        super(NullBooleanField, self).__init__(*args, **kwargs)


class PositiveIntegerField(raw_models.PositiveIntegerField):
    def __init__(self, *args, **kwargs):
        super(PositiveIntegerField, self).__init__(*args, **kwargs)


class PositiveSmallIntegerField(raw_models.PositiveSmallIntegerField):
    def __init__(self, *args, **kwargs):
        super(PositiveSmallIntegerField, self).__init__(*args, **kwargs)


class SlugField(raw_models.SlugField):
    def __init__(self, *args, **kwargs):
        super(SlugField, self).__init__(*args, **kwargs)


class SmallIntegerField(raw_models.SmallIntegerField):
    def __init__(self, *args, **kwargs):
        super(SmallIntegerField, self).__init__(*args, **kwargs)


class TextField(raw_models.TextField):
    def __init__(self, null=True, blank=True, *args, **kwargs):
        kwargs['null'] = null
        kwargs['blank'] = blank
        super(TextField, self).__init__(*args, **kwargs)


class TimeField(raw_models.TimeField):
    def __init__(self, *args, **kwargs):
        super(TimeField, self).__init__(*args, **kwargs)


class URLField(raw_models.URLField):
    def __init__(self, max_length=1024, *args, **kwargs):
        kwargs['max_length'] = max_length
        super(URLField, self).__init__(*args, **kwargs)


class ForeignKey(raw_models.ForeignKey):
    def __init__(self, to=None, on_delete=None, **kwargs):
        super(ForeignKey, self).__init__(to, on_delete, **kwargs)


class ManyToManyField(raw_models.ManyToManyField):
    def __init__(self, to, **kwargs):
        super(ManyToManyField, self).__init__(to, **kwargs)


class OneToOneField(raw_models.OneToOneField):
    def __init__(self, to, to_field=None, **kwargs):
        super(OneToOneField, self).__init__(to, to_field=None, **kwargs)