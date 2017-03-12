import json
import functools

import ioc.loader
import yaml


class Codec:
    """A class that encodes/decodes multiple content types."""
    Unknown = type('Unknown', (Exception,), {})
    Undecodable = type('Undecodable', (Unknown,), {})
    Unencodable = type('Unencodable', (Unknown,), {})

    @classmethod
    def fromqualnames(cls, qualnames):
        """Create a new :class:`Codec` instance configured with
        the encoders/decoders specified by list `qualnames`.
        """
        return cls([ioc.loader.import_symbol(x) for x in qualnames])

    def __init__(self, codecs=None):
        codecs = codecs or []
        codecs.extend([
            YAMLDecoder(),
            YAMLEncoder(),
            JSONDecoder(),
            JSONEncoder()
        ])

        self.encoders = [x for x in codecs if x.is_encoder()]
        self.decoders = [x for x in codecs if x.is_decoder()]


    def encode(self, mimetype, payload):
        """Encode `payload` using the `mimetype` as a hint for the
        serializers.
        """
        codec = sentinel = object()
        for candidate in self.encoders:
            if not candidate.can_encode(mimetype, payload):
                continue
            codec = candidate
            break

        if codec == sentinel:
            raise self.Unencodable(mimetype)
    
        try:
            f = functools.partial(codec.encode, mimetype)

            return f(payload)\
                if not hasattr(payload, '__serialize__')\
                else payload.__serialize__(f)
        except Exception as e:
            raise self.Unencodable(e)

    def decode(self, mimetype, payload):
        """Decode `payload` using the `mimetype` as a hint for the
        deserializers.
        """
        codec = sentinel = object()
        for candidate in self.decoders:
            if not candidate.can_decode(mimetype, payload):
                continue
            codec = candidate
            break

        if codec == sentinel:
            raise self.Undecodable(mimetype)
    
        try:
            return codec.decode(mimetype, payload)
        except Exception as e:
            raise self.Undecodable(e)


class BaseEncoder:
    """The base class for all encoders."""
    content_type = object()

    def is_encoder(self):
        return True

    def is_decoder(self):
        return False

    def encode(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must override this method.")

    def can_encode(self, mimetype, obj):
        return mimetype == self.content_type


class BaseDecoder:
    """The base class for all decoders."""
    content_type = object()

    def can_decode(self, mimetype, seq):
        return mimetype == self.content_type\
            and isinstance(seq, (str, bytes))

    def is_encoder(self):
        return False

    def is_decoder(self):
        return True

    def decode(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must override this method.")


class YAMLDecoder(BaseDecoder):
    content_type = "application/yaml"

    def decode(self, mimetype, seq):
        if isinstance(seq, bytes):
            seq = seq.decode('utf8')
        return yaml.safe_load(seq)


class JSONDecoder(BaseDecoder):
    content_type = "application/json"

    def decode(self, mimetype, seq):
        if isinstance(seq, bytes):
            seq = seq.decode('utf8')
        return json.loads(seq)


class YAMLEncoder(BaseEncoder):
    content_type = "application/yaml"

    def encode(self, mimetype, obj):
        return yaml.safe_dump(obj, indent=2,
            default_flow_style=False)


class JSONEncoder(BaseEncoder):
    content_type = "application/json"

    def encode(self, mimetype, obj):
        return json.dumps(obj, indent=4, sort_keys=True)
