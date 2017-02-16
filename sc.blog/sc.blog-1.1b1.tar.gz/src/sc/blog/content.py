# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from sc.blog import _
from zope import schema
from zope.interface import implementer


class IBlog(model.Schema):
    """A Blog."""

    author = schema.TextLine(
        title=_(u'Author'),
        default=u'',
    )

    image = NamedBlobImage(
        title=_(u'Image'),
        required=False,
    )


@implementer(IBlog)
class Blog(Container):
    """A Blog."""


def blog_added(ob, event):
    """ handler for IObjectAddedEvent
        here we revoke "sc.blog: Add Blog" permission and acquisition
        this way Blogs couldn't be added inside Blogs or subobjects
        of Blogs.
    """
    # inside blogs you can't add blogs
    ob.manage_permission('sc.blog: Add Blog')
