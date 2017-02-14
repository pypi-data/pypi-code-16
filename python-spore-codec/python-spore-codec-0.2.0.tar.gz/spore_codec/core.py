import json

from coreapi import Link as BaseLink
from coreapi.codecs.base import BaseCodec
from coreapi.compat import COMPACT_SEPARATORS, VERBOSE_SEPARATORS
from coreapi.compat import force_bytes
from coreapi.document import Document
from .encode import generate_spore_object


class SporeDescriptionCodec(BaseCodec):

    media_type = 'application/sporeapi+json'
    format = 'spore'

    def decode(self, bytestring, **options):
        pass

    def encode(self, document, **options):
        if not isinstance(document, Document):
            raise TypeError('Expected a `coreapi.Document` instance')

        indent = options.get('indent', None)

        kwargs = {
            'ensure_ascii': False, 'indent': indent,
            'separators': indent and VERBOSE_SEPARATORS or COMPACT_SEPARATORS
        }

        global_formats = options.get('formats', [])
        spore_settings = options.get('settings', [])

        data = generate_spore_object(document, global_formats, spore_settings)
        return force_bytes(json.dumps(data, **kwargs))


class Link(BaseLink):

    def __init__(self, url=None, action=None, encoding=None,
                 transform=None, title=None, description=None, fields=None,
                 authentication=None, formats=None):
        super().__init__(url, action, encoding, transform, title, description,
                         fields)
        if (authentication is not None) and (not isinstance(authentication,
                                                            bool)):
            raise TypeError("Argument 'authentication' must be a boolean.")
        if (formats is not None) and (not isinstance(formats, (list, tuple))):
            raise TypeError("Argument 'formats' must be a list.")

        self._authentication = (False if (authentication is None) else
                             authentication)
        self._formats = () if (formats is None) else formats


    @classmethod
    def from_base_link(cls, link, authentication, formats):
        instance = cls(link.url, link.action, link.encoding, link.transform,
                       link.title, link.description, link.fields,
                       authentication, formats)
        del link
        return instance

    @property
    def authentication(self):
        return self._authentication

    @property
    def formats(self):
        return self._formats
