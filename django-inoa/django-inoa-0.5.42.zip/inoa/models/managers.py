# -*- coding: utf-8 -*-

from django.db import models

class SelectRelatedManager(models.Manager):
    """
    A Manager whose querysets always include select_related() by default.
    Parameters passed in the constructor will be used directly in select_related.
    """
    def get_queryset(self):
        return super(SelectRelatedManager, self).get_queryset().select_related(*self.args, **self.kwargs)

    def __init__(self, *args, **kwargs):
        super(SelectRelatedManager, self).__init__()
        self.args = args
        self.kwargs = kwargs

class FilterManager(models.Manager):
    """
    A Manager whose querysets will filter the object by default.
    Parameters passed in the constructor will be used directly in filter().)
    """
    def get_queryset(self):
        return super(FilterManager, self).get_queryset().filter(*self.args, **self.kwargs)

    def __init__(self, *args, **kwargs):
        super(FilterManager, self).__init__()
        self.args = args
        self.kwargs = kwargs

class ExcludeManager(models.Manager):
    """
    A Manager whose querysets will filter the object by default.
    Parameters passed in the constructor will be used directly in exclude().)
    """
    def get_queryset(self):
        return super(ExcludeManager, self).get_queryset().exclude(*self.args, **self.kwargs)

    def __init__(self, *args, **kwargs):
        super(ExcludeManager, self).__init__()
        self.args = args
        self.kwargs = kwargs
