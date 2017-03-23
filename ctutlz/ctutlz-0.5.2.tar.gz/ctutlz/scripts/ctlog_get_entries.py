'''Retrieve an entry from a Certificate Transparency Log (ct-log),
cf. https://tools.ietf.org/html/rfc6962#section-4.6
'''

import argparse
import logging

import requests
from utlz import flo, first_paragraph, namedtuple

from ctutlz.utils.encoding import decode_from_b64
from ctutlz.utils.logger import setup_logging
from ctutlz.utils.string import string_with_prefix


def create_parser():
    parser = argparse.ArgumentParser(description=first_paragraph(__doc__))
    meg = parser.add_mutually_exclusive_group()
    meg.add_argument('--short',
                     dest='loglevel',
                     action='store_const',
                     const=logging.WARNING,
                     default=logging.INFO,  # default loglevel if nothing set
                     help='show short result and warnings/errors only')
    meg.add_argument('--debug',
                     dest='loglevel',
                     action='store_const',
                     const=logging.DEBUG,
                     help='show more for diagnostic purposes')

    req = parser.add_argument_group('required arguments')
    req.add_argument('--log',
                     metavar='<url>',
                     required=True,
                     help='ct-log to retrieve '
                          '(example: `ct.googleapis.com/pilot`; cf. '
                          'https://www.certificate-transparency.org/'
                          'known-logs)')
    req.add_argument('--entry',
                     metavar='<dec>',
                     required=True,
                     help='zero-based decimal index of the log entry '
                          'to retrieve')
    return parser


# https://tools.ietf.org/html/rfc6962#section-3.4

# tdf := TLS Data Formatting (cf. https://tools.ietf.org/html/rfc5246#section-4)


_TimestampedEntry = namedtuple(
    typename='TimestampedEntry',
    field_names=[
        'tdf',

        'timestamp',
        'entry_type',
        'signed_entry',
        'extensions',
    ],
)


def TimestampedEntry(tdf):
    return _TimestampedEntry(tdf, None, None, None, None)  # TODO


_MerkleTreeLeaf = namedtuple(
    typename='MerkleTreeLeaf',
    field_names=[
        'tdf',

        'version',
        'entry',
        'leaf_type="timestamped_entry"',
    ],
    lazy_vals={
        'timestamped_entry': lambda self: self.leaf_type,
    }
)


def MerkleTreeLeaf(tdf):
    return _MerkleTreeLeaf(tdf, None, None, None)  # TODO


LogEntry = namedtuple(
    typename='LogEntry',
    field_names=[
        'as_dict',
    ],
    lazy_vals={
        'leaf_input_b64': lambda self: self.as_dict['leaf_input'],
        'leaf_input_tdf': lambda self: decode_from_b64(self.leaf_input_b64),
        'leaf_input': lambda self: MerkleTreeLeaf(self.leaf_input_tdf),

        'is_precert_chain_entry': lambda self: not self.is_x509_chain_entry,
        'is_x509_chain_entry': lambda self:
            self.leaf_input.timestamped_entry.entry_type == 0,  # TODO

        'extra_data_b64': lambda self: self.as_dict['extra_data'],
        'extra_data_tdf': lambda self: decode_from_b64(self.extra_data_b64),
        'extra_data': lambda self: None,  # TODO
    }
)


GetEntriesResponse = namedtuple(
    typename='GetEntriesResponse',
    field_names=[
        'as_dict',
    ],
    lazy_vals={
        'entries': lambda self: [LogEntry(entry)
                                 for entry
                                 in self.as_dict['entries']],
        'first_entry': lambda self: self.entries[0],
    },
)


def get_entry(index, ctlog_url):
    url = string_with_prefix('https://', ctlog_url) + '/ct/v1/get-entries'
    payload = {'start': index, 'end': index}
    req = requests.get(url, params=payload)
    if req.ok:
        response = GetEntriesResponse(as_dict=req.json())

        print(response.first_entry.leaf_input)


def main():
    parser = create_parser()
    args = parser.parse_args()
    logger = setup_logging(args.loglevel)
    logger.debug(args)

    get_entry(index=args.entry, ctlog_url=args.log)


if __name__ == '__main__':
    main()
