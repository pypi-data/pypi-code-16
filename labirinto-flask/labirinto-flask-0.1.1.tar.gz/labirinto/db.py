# -*- coding: utf-8 -*-

from flask_mongoengine import MongoEngine
from mongoengine.queryset import DoesNotExist, MultipleObjectsReturned, QuerySet


db = MongoEngine()
