#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.ext import ndb


class BasicAuth(ndb.Model):
    """Client Model."""
    user = ndb.StringProperty(required=True)
    password = ndb.StringProperty(required=True)
    status = ndb.BooleanProperty(required=True,default=True)
