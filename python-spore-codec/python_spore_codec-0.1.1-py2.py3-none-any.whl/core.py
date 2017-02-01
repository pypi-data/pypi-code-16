import json

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

        data = generate_spore_object(document)
        return force_bytes(json.dumps(data, **kwargs))
