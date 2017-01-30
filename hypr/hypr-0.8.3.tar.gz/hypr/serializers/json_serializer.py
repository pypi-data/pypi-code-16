# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""JSON serializer."""
import json
from datetime import tzinfo, timedelta


class _simple_utc(tzinfo):  # pragma: no cover

    def tzname(self):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)


def encoder(obj):
    """Json encoder."""
    # handle date[time] objects
    if hasattr(obj, 'strftime'):
        if hasattr(obj, 'hour'):
            return obj.replace(tzinfo=_simple_utc()).isoformat()
        else:
            return '%sT00:00:00+00:00' % obj.isoformat()

    # handle uuid objects
    if hasattr(obj, 'hex'):
        return str(obj)

    # handle serializable objects
    if hasattr(obj, '__serialize__'):
        return obj.__serialize__()

    raise TypeError('%s is not JSON serializable.' % repr(obj))


def json_serializer(obj, request=None, default=None):
    """Json serializer."""
    pretty_print = False
    if request is not None:
        pretty_print = request.args.get('_pprint', '').lower() in ('true', '1')

    indent = None
    if pretty_print:    # pragma: no cover
        indent = 4

    if default is None:
        default = encoder

    return json.dumps(obj, default=default, sort_keys=True, indent=indent)
