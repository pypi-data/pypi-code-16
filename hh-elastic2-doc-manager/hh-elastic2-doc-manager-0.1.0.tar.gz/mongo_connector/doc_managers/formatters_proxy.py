import base64
import datetime
import re

from uuid import UUID
from math import isnan, isinf

import logging
LOG = logging.getLogger(__name__)


import bson
import bson.json_util

from mongo_connector.compat import PY3

if PY3:
    long = int
    unicode = str

RE_TYPE = type(re.compile(""))
try:
    from bson.regex import Regex
    RE_TYPES = (RE_TYPE, Regex)
except ImportError:
    RE_TYPES = (RE_TYPE,)


class DocumentFormatter(object):
    """Interface for classes that can transform documents to conform to
    external drivers' expectations.
    """

    def transform_value(self, value,namespace):
        """Transform a leaf-node in a document.

        This method may be overridden to provide custom handling for specific
        types of values.
        """
        raise NotImplementedError

    def transform_key(self, key,namespace):
        """Transform a leaf-node in a document.

        This method may be overridden to provide custom handling for specific
        types of values.
        """
        raise NotImplementedError

    def transform_element(self, key, value,namespace):
        """Transform a single key-value pair within a document.

        This method may be overridden to provide custom handling for specific
        types of values. This method should return an iterator over the
        resulting key-value pairs.
        """
        raise NotImplementedError

    def format_document(self, document,namespace):
        """Format a document in preparation to be sent to an external driver."""
        raise NotImplementedError

class DocumentFormatterProxy(DocumentFormatter):
    def __init__(self,kwargs):
	self.formatter = DefaultDocumentFormatter(kwargs)

    def transform_value(self, value,namespace):
	return self.formatter.transform_value(value,namespace)

    def transform_key(self, key,namespace):
        return self.formatter.transform_key(key,namespace)

    def transform_element(self, key, value,namespace):
        return self.formatter.transform_element(key, value,namespace)

    def format_document(self, document,namespace):
        a = self.formatter.format_document(document,namespace)
	print a
	return a


class DefaultDocumentFormatter(DocumentFormatterProxy):
    """Basic DocumentFormatter that preserves numbers, base64-encodes binary,
    and stringifies everything else.
    """
    def __init__(self,option):
	self.format_option = option

    def transform_value(self, value,namespace):
        # This is largely taken from bson.json_util.default, though not the same
        # so we don't modify the structure of the document
        if isinstance(value, dict):
            return self.format_document(value)
        elif isinstance(value, list):
            return [self.transform_value(v,namespace) for v in value]
        if isinstance(value, RE_TYPES):
            flags = ""
            if value.flags & re.IGNORECASE:
                flags += "i"
            if value.flags & re.LOCALE:
                flags += "l"
            if value.flags & re.MULTILINE:
                flags += "m"
            if value.flags & re.DOTALL:
                flags += "s"
            if value.flags & re.UNICODE:
                flags += "u"
            if value.flags & re.VERBOSE:
                flags += "x"
            pattern = value.pattern
            # quasi-JavaScript notation (may include non-standard flags)
            return '/%s/%s' % (pattern, flags)
        elif (isinstance(value, bson.Binary) or
              (PY3 and isinstance(value, bytes))):
            # Just include body of binary data without subtype
            return base64.b64encode(value).decode()
        elif isinstance(value, UUID):
            return value.hex
        elif isinstance(value, (int, long, float)):
            if isnan(value):
                raise ValueError("nan")
            elif isinf(value):
                raise ValueError("inf")
            return value
        elif isinstance(value, datetime.datetime):
            return value
        elif value is None:
            return value
        # Default
        return unicode(value)


    def transform_key(self, key,namespace):
	if namespace in self.format_option:
		fmap = self.format_option.get(namespace,{})
		if key in fmap:
		    return fmap.get(key,key)	
	return key;


    def transform_element(self, key, value,namespace):
        try:
            new_value = self.transform_value(value,namespace)
            new_key = self.transform_key(key,namespace)
            yield new_key, new_value
        except ValueError as e:
            LOG.warn("Invalid value for key: %s as %s"
                     % (key, str(e)))

    def format_document(self, document,namespace):
        def _kernel(doc):
            for key in doc:
                value = doc[key]
                for new_k, new_v in self.transform_element(key, value,namespace):
                    yield new_k, new_v
        return dict(_kernel(document))


class DocumentFlattener(DefaultDocumentFormatter):
    """Formatter that completely flattens documents and unwinds arrays:

    An example:
      {"a": 2,
       "b": {
         "c": {
           "d": 5
         }
       },
       "e": [6, 7, 8]
      }

    becomes:
      {"a": 2, "b.c.d": 5, "e.0": 6, "e.1": 7, "e.2": 8}

    """

    def transform_element(self, key, value,namespace):
        if isinstance(value, list):
            for li, lv in enumerate(value):
                for inner_k, inner_v in self.transform_element(
                        "%s.%s" % (key, li), lv,namespace):
                    yield inner_k, inner_v
        elif isinstance(value, dict):
            formatted = self.format_document(value,namespace)
            for doc_key in formatted:
                yield "%s.%s" % (key, doc_key), formatted[doc_key]
        else:
            # We assume that transform_value will return a 'flat' value,
            # not a list or dict
            yield key, self.transform_value(value,namespace)

    def format_document(self, document,namespace):
        def flatten(doc, path):
            top_level = (len(path) == 0)
            if not top_level:
                path_string = ".".join(path)
            for k in doc:
                v = doc[k]
                if isinstance(v, dict):
                    path.append(k)
                    for inner_k, inner_v in flatten(v, path):
                        yield inner_k, inner_v
                    path.pop()
                else:
                    transformed = self.transform_element(k, v,namespace)
                    for new_k, new_v in transformed:
                        if top_level:
                            yield new_k, new_v
                        else:
                            yield "%s.%s" % (path_string, new_k), new_v
        return dict(flatten(document, []))
