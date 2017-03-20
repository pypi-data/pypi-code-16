# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from ..sqlite import PickleField
from peewee import Model, TextField, BlobField


class Metadataset(Model):
    name = TextField()
    metadata = PickleField()
    data = PickleField()
