# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""A parser for the Accept header."""


import re


accept_range = re.compile(r'''
    (?P<type>\S+)/                                    # mandatory type
    (?:(?P<vendor>[^\s;+]+)\.)?                       # optional vendor
    (?P<subtype>[^\s;+]+(?:[^\s;]+)?)                 # mandatory subtype
    (?:;(?:(?:[ ]*q=(?P<quality>\d(?:\.\d)?))|(?:[^s;]+=[^s;]+)))*  # quality
''', re.VERBOSE)


def parse_accept_header(accept):
    """Parse the accept header.

    Each accepted media type is yielded as a tuple with the type, subtype and
    quality. If the quality is not set, it is defaulted to 1.
    """
    for media_range in accept.split(','):
        match = accept_range.match(media_range.strip())
        if match is None:
            break

        data = match.groupdict()
        yield (data['type'], data['subtype'], float(data['quality'] or 1.0))


def choose_media_type(accept, available):
    """Choose the best available media type to satisfy the accept header.

    Args:
        accept (str): an HTTP Accept header (RFC 2616).
        available (list): a list of valid media types (RFC 6838).
    Returns:
        the most well suited media type.
    """
    rv = []
    for type_, subtype, quality in parse_accept_header(accept):
        media_type = '%s/%s' % (type_, subtype)
        if media_type in available:
            if quality == 1:
                return media_type   # a best solution has been found
            else:
                rv.append((quality, media_type))

        # the wildcards are used to set a default quality to the remaining
        # media types available. if a wildcard has the same quality of an
        # accepted media type, the quality of the former is lowered to promote
        # the latter. For a given quality the order is as follow :
        # explicit media type > wildcard on the subtype > wilcard on the type
        elif '*' in media_type:
            for media_type in available:
                if type_ == '*' and media_type not in rv:
                    rv.append((quality - 0.02, media_type))
                elif media_type.startswith(type_) and media_type not in rv:
                    rv.append((quality - 0.01, media_type))

    if rv:
        rv.sort(key=lambda x: -x[0])
        return rv[0][1]
