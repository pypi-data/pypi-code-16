#!/usr/bin/python
# -*- coding: utf-8 -*-
from ferris3 import BasicModel
from google.appengine.ext import ndb


class BasicAuth(BasicModel):
    """Client Model."""
    user = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    status = ndb.BooleanProperty(required=True,default=True)
