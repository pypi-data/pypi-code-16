from zope.interface import implementer
from zope.annotation import IAnnotations
from souper.interfaces import IStorageLocator
from souper.soup import SoupData

CACHE_PREFIX = 'soup_storage_%s'
SOUPPATHS = 'SOUPPATHS'
SOUPKEY = 'SOUP-%s'


@implementer(IStorageLocator)
class StorageLocator(object):

    def __init__(self, context):
        self.root = context

    def storage(self, sid):
        """return SoupData for the given soup id
        """
        context = self.traverse(self.path(sid))
        return self.soupdata(context, sid)

    def path(self, sid):
        """path to object with soupdata annotations for given soup id.
        relative to root.
        """
        paths = IAnnotations(self.root).get(SOUPPATHS, {})
        return paths.get(sid, '/')

    def traverse(self, path):
        """traverse to path relative to soups root and return the object there.
        """
        obj = self.root
        path = [_ for _ in path.split('/') if _]
        for name in path:
            try:
                obj = obj[name]
            except AttributeError:
                msg = u'Object at %s does not exist.' % '/'.join(path)
                raise ValueError(msg)
        return obj

    def soupdata(self, obj, sid):
        """fetches the soup data from objects annotations.
        """
        key = SOUPKEY % sid
        annotations = IAnnotations(obj)
        if key not in annotations:
            annotations[key] = SoupData()
        return annotations[key]
