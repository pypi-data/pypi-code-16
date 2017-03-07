
# Copyright (c) 2009 - 2016, UChicago Argonne, LLC.
# See LICENSE file for details.

'''
common tools used in various places

for more information on the various codepoints, see
https://docs.python.org/2/library/codecs.html#standard-encodings
'''

XML_CODEPOINT = 'ISO-8859-1'
CODEPOINT_LIST = ('utf8 ascii utf16 utf32'.split()
                  + ['cp125'+str(i) for i in range(9)]
                  + ['latin'+str(i+1) for i in range(10)])


def text_decode(source):
    '''try decoding ``source`` with various known codepoints to unicode'''
    for encoding in CODEPOINT_LIST:  # walk through a list of codepoints
        try:
            return source.decode(encoding, 'replace')
        except (ValueError, UnicodeError) as _exc:
            continue
        except Exception as _exc:
            continue
    return source


def text_encode(source):
    '''encode ``source`` using the default codepoint'''
    return source.encode(encoding=XML_CODEPOINT, errors='ignore')
