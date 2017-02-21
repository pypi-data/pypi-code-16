import logging
import inspect
import json
from datetime import datetime
from zope.publisher.browser import BrowserView
from Products.PageTemplates.PageTemplate import PageTemplate
from edw.logger.util import get_ip

logger = logging.getLogger("edw.logger")

IGNORED_CTS = (
    'text/css',
    'image/',
    'javascript',
    'font',
)

KNOWN_METHODS = ('GET', 'POST')


def skip_contenttype(content_type):
    if not content_type:
        return
    for ct in IGNORED_CTS:
        if ct in content_type:
            return True


def traverse_wrapper(meth):
    """Extract some basic info about the object and view. traverse method
    gives us access to the traversed object"""

    def extract(self, *args, **kwargs):
        try:
            obj = meth(self, *args, **kwargs)
            try:
                if self.method not in KNOWN_METHODS:
                    # Ignore requests we don't handle.
                    # Things like HEAD and OPTIONS from health checkers
                    # can really spam the log.
                    return obj
                user = self.get('AUTHENTICATED_USER')
                username = user.getUserName()
                if username == 'Anonymous User':
                    partition = 'Anonymous'
                else:
                    partition = 'Authenticated'

                kv = {
                    'User': username,
                    'IP': get_ip(self),
                    'URL': self.URL,
                    'ACTUAL_URL': self.ACTUAL_URL,
                    'Partition': partition,
                    'Type': 'Traverse',
                    'Date': datetime.now().isoformat(),
                    'LoggerName': logger.name
                }

                # Old school CMF style page template
                if isinstance(obj, PageTemplate):
                    kv['Action'] = obj.getId()
                    kv['Template'] = obj.pt_source_file()
                    parent = obj.getParentNode()
                    kv['Controller'] = parent.meta_type
                    kv['Object'] = parent.absolute_url()

                # Z3 style views
                elif isinstance(obj, BrowserView):
                    kv['Action'] = obj.__name__
                    if hasattr(obj.context, 'meta_type'):
                        kv['Controller'] = obj.context.meta_type
                    kv['Object'] = obj.context.absolute_url()

                # ZMI
                elif inspect.ismethod(obj):
                    # skip content type based on file content type
                    content_type = getattr(obj.im_self, 'content_type', None)
                    if skip_contenttype(content_type):
                        return obj

                    if hasattr(obj.im_self, 'meta_type'):
                        kv['Controller'] = obj.im_self.meta_type

                else:
                    kv['Controller'] = obj.aq_parent.meta_type

                if 'Controller' not in kv:
                    return obj

                # skip content type based on request header
                if not skip_contenttype(self.HTTP_ACCEPT):
                    logger.info(json.dumps(kv))

                return obj
            except:
                return obj

        except:
            raise

    return extract


from ZPublisher.BaseRequest import BaseRequest

BaseRequest.orig_traverse = BaseRequest.traverse
BaseRequest.traverse = traverse_wrapper(BaseRequest.orig_traverse)
