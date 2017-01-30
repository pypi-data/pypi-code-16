#  Copyright 2016-2017 Luigi Mori
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
This module implements a parser for Snort rules based on Perl Snort::Rule
"""

import re
import logging
from collections import namedtuple


__all__ = ['Rule', 'parse_rules', 'tokenize_opts']


LOG = logging.getLogger(__name__)


CONTENT_MODIFIERS = [
    'nocase',
    'rawbytes',
    'depth',
    'offset',
    'distance',
    'within',
    'http_client_body',
    'http_cookie',
    'http_raw_cookie',
    'http_header',
    'http_raw_header',
    'http_method',
    'http_uri',
    'http_raw_uri',
    'http_stat_code',
    'http_stat_msg',
    'fast_pattern',
]

URICONTENT_MODIFIERS = [
    'nocase',
    'depth',
    'offset',
    'distance',
    'within',
    'fast_pattern'
]

SINGLE_OPTS = [
    # general options
    'msg',
    'reference',
    'sid',
    'rev',
    'gid',
    'classtype',
    'priority',

    # payload detection options
    'urilen',  # XXX should be parsed
    'flowbits',  # XXX should be parsed
    'file_data',
    'pkt_data',
    'isdataat',  # XXX should be parsed
    'byte_test',
    'byte_jump',
    'byte_extract',
    'base64_decode',
    'base64_data',
    'ssl_state',

    # non-payload detection options
    'flags',
    'dsize',
    'itype',
    'icode',
    'stream_size',
    'icmp_id',

    # post-detection options
    'detection_filter',  # XXX rate check, should be parsed
    'tag',  # XXX should be parsed

    # thresholds
    'threshold'  # XXX should be parsed
]

RULE_ACTIONS = [
    'alert',
    'pass',
    'drop',
    'sdrop',
    'log',
    'activate',
    'dynamic',
    'reject'
]

RULE_ELEMENTS_REQUIRED = [
    'action',
    'proto',
    'src',
    'src_port',
    'direction',
    'dst',
    'dst_port'
]

RULE_ELEMENTS = RULE_ELEMENTS_REQUIRED + ['opts']

_SPLIT_OPTS_RE = re.compile("""\s*         # ignore preceeding whitespace
                               (           # begin capturing
                                    (?:        # grab characters we want
                                        \\\\.    # skip over escapes
                                        |
                                        [^;]   # or anything but a ;
                                    )+?        # ? greedyness hack lets the \s* actually match
                                )           # end capturing
                                \s*         # ignore whitespace between value and ; or end of line
                                (?:         # stop anchor at ...
                                    ;         # semicolon
                                    |         # or
                                    $         # end of line
                                )
                                \s*""", re.X)


_BaseRuleOption = namedtuple(
    'RuleOption',
    field_names=['option', 'arguments', 'modifiers']
)


class RuleOption(_BaseRuleOption):
    def __new__(_cls, option, arguments, modifiers=None):
        return _BaseRuleOption.__new__(_cls, option, arguments, modifiers)


_BaseRule = namedtuple(
    '_BaseSnortRule',
    field_names=RULE_ELEMENTS
)


class Rule(_BaseRule):
    def get_opt(self, key, default=None):
        return next(
            (o[1] for o in self.get('opts', []) if o[0] == key),
            default
        )

    def tokenize_opts(self):
        return tokenize_opts(self.opts)

    @classmethod
    def parse(cls, rule):
        elements = {}

        rule = rule.strip()

        values = rule.split(None, len(RULE_ELEMENTS)-1)

        # parse basic elements
        for n, e in enumerate(RULE_ELEMENTS_REQUIRED):
            elements[e] = values[n]

        # parse options
        opts = values[-1]
        if opts[0] == '(':
            if opts[-1] != ')':
                raise RuntimeError(
                    'rule is missing closing parenthesis: %s' % opts[-1]
                )
            opts = opts[1:-1]

        split_opts = map(
            lambda x: x.split(':', 1),
            _SPLIT_OPTS_RE.findall(opts)
        )

        elements['opts'] = split_opts

        return cls(**elements)


def parse_rules(f):
    NORMAL = 0
    IN_COMMENT = 1

    state = NORMAL
    for l in f:
        l = l.strip()

        if state == IN_COMMENT:
            if l.startswith('#-'):
                state = NORMAL
            continue

        if not l:
            continue

        if l.startswith('#-'):
            state = IN_COMMENT
            continue

        if l[0] == '#' and not l.startswith('# alert'):
            continue

        if l.startswith('# alert'):
            l = l[2:]

        yield Rule.parse(l)

    if state != NORMAL:
        raise RuntimeError('still in comment at the end of file')


def _normalize_content(content):
    NORMAL = 0
    IN_ESCAPE = 1
    IN_PIPE = 2

    result = {
        'not': False,
        'content': ''
    }

    state = NORMAL

    content = content.strip()

    if content[0] == '!':
        result['not'] = True
        content = content[1:]

    if content[0] != '"':
        raise RuntimeError('unknown content format: %s' % content)
    content = content[1:-1]

    new_content = ''
    idx = 0
    while idx < len(content):
        c = content[idx]

        if state == IN_ESCAPE:
            new_content += c
            state = NORMAL
            idx += 1
            continue

        if state == IN_PIPE:
            next_pipe_idx = content[idx:].index('|')
            byte_string = content[idx:idx + next_pipe_idx]
            idx += next_pipe_idx

            bytes = ''.join(byte_string.split())
            new_content += bytes.decode('hex')
            state = NORMAL
            idx += 1
            continue

        if c == '\\':
            state = IN_ESCAPE
            idx += 1
            continue

        if c == '|':
            state = IN_PIPE
            idx += 1
            continue

        new_content += c
        idx += 1

    if state != NORMAL:
        raise RuntimeError('strange content string: %s' % content)

    result['content'] = new_content

    return result


def tokenize_opts(opts):
    current_content = None

    for o in opts:
        oname = o[0]

        ovalue = None
        if len(o) > 1:
            ovalue = o[1]

        if oname in URICONTENT_MODIFIERS:
            if current_content is None:
                raise RuntimeError('content modifier with no preceding (uri)content')

            current_content.modifiers[oname] = ovalue
            continue

        if oname in CONTENT_MODIFIERS:
            if current_content is None:
                raise RuntimeError('content modifier with no preceding content')

            current_content.modifiers[oname] = ovalue
            continue

        if oname in SINGLE_OPTS:
            yield RuleOption(option=oname, arguments=ovalue)
            continue

        if oname == 'content':
            if current_content is not None:
                yield current_content
                current_content = None

            content = _normalize_content(ovalue)

            current_content = RuleOption(
                option='content',
                arguments=content,
                modifiers={}
            )

            continue

        if oname == 'uricontent':
            if current_content is not None:
                yield current_content
                current_content = None

            content = _normalize_content(ovalue)

            current_content = RuleOption(
                option='uricontent',
                arguments=content,
                modifiers={}
            )

            continue

        if oname == 'metadata':
            KVs = [kv.strip() for kv in ovalue.split(',')]
            KVs = [kv.split(None, 1) for kv in KVs]

            yield RuleOption(
                option='metadata',
                arguments={k: v for k, v in KVs}
            )
            continue

        if oname == 'flow':
            _options = {_o.strip(): True for _o in ovalue.split(',')}

            yield RuleOption(option='flow', arguments=_options)
            continue

        if oname == 'pcre':
            # XXX analyze PCRE
            yield RuleOption(option='pcre', arguments=ovalue)
            continue

        raise RuntimeError('Unhandled option: {} - {}'.format(oname, opts))
