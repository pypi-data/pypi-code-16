### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import standard packages
from datetime import datetime
from fanstatic import Library, Resource

import re

# import Zope3 interfaces
from transaction.interfaces import ITransactionManager
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.extfile.interfaces import IBaseBlobFile

# import Zope3 packages
import zope.datetime

# import local packages
from ztfy.jqueryui import jquery_imgareaselect
from zope.security.proxy import removeSecurityProxy


library = Library('ztfy.file', 'resources')

ztfy_file = Resource(library, 'js/ztfy.file.js', minified='js/ztfy.file.min.js',
                     depends=[jquery_imgareaselect], bottom=True)


_rx_range = re.compile('bytes *= *(\d*) *- *(\d*)', flags=re.I)

MAX_RANGE_LENGTH = 1 << 21  # 2 Mb


class Range(object):
    """Range header value parser

    Copied from Pyramid...
    """
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @classmethod
    def parse(cls, request):
        range = request.getHeader('Range')
        if range is None:
            return None
        m = _rx_range.match(range)
        if not m:
            return None
        start, end = m.groups()
        if not start:
            return cls(-int(end), None)
        start = int(start)
        if not end:
            return cls(start, None)
        end = int(end) + 1
        if start >= end:
            return None
        return cls(start, end)


class FileView(object):

    def show(self):
        """This is just a refactoring of original zope.app.file.browser.file.FileView class,
        which according to me didn't handle last modification time correctly...
        """
        context = self.context
        request = self.request
        response = request.response

        if request is not None:
            header = response.getHeader('Content-Type')
            if header is None:
                response.setHeader('Content-Type', context.contentType)
            response.setHeader('Content-Length', context.getSize())

        try:
            modified = IZopeDublinCore(context).modified
        except TypeError:
            modified = None
        if modified is None or not isinstance(modified, datetime):
            return context.data

        # check for last modification date
        header = request.getHeader('If-Modified-Since', None)
        lmt = long(zope.datetime.time(modified.isoformat()))
        if header is not None:
            header = header.split(';')[0]
            try:
                mod_since = long(zope.datetime.time(header))
            except:
                mod_since = None
            if mod_since is not None:
                if lmt <= mod_since:
                    response.setStatus(304)
                    return ''
        response.setHeader('Last-Modified', zope.datetime.rfc1123_date(lmt))

        # check content range on blobs
        if IBaseBlobFile.providedBy(context):
            # Commit transaction to avoid uncommitted blobs error while generating display
            ITransactionManager(removeSecurityProxy(context)).get().commit()
            body_file = removeSecurityProxy(context.getBlob(mode='c'))
            body_length = context.getSize()
            range = Range.parse(request)
            if range is not None:
                response.setStatus(206)  # Partial content
                range_start = range.start or 0
                body_file.seek(range_start)
                if 'Firefox' in request.getHeader('User-Agent'):
                    range_end = range.end or body_length
                    response.setHeader('Content-Range',
                                       'bytes {first}-{last}/{len}'.format(first=range_start,
                                                                           last=range_end - 1,
                                                                           len=body_length))
                    response.setHeader('Content-Length', range_end - range_start)
                    return body_file
                else:
                    range_end = range.end or min(body_length, range_start + MAX_RANGE_LENGTH)
                    ranged_body = body_file.read(range_end - range_start)
                    response.setHeader('Content-Range',
                                       'bytes {first}-{last}/{len}'.format(first=range_start,
                                                                           last=range_start + len(ranged_body) - 1,
                                                                           len=body_length))
                    return ranged_body
            else:
                return body_file
        else:
            return context.data
