# -*- coding: utf-8 -*-

"""
Created on 2016-10-18
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

from kotti.interfaces import IDefaultWorkflow
from kotti.resources import Content
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Unicode
from zope.interface import implements

from kotti_contenttypes import _


class Folder(Content):
    """ A custom content type. """

    implements(IDefaultWorkflow)

    id = Column(Integer, ForeignKey('contents.id'), primary_key=True)

    type_info = Content.type_info.copy(
        name=u'Folder',
        title=_(u'Folder'),
        add_view=u'add_folder',
        addable_to=[u'Document', 'Folder']
    )
