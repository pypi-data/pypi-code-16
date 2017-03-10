import uuid
import six
from datetime import datetime
from io import BytesIO

from warcio.timeutils import datetime_to_iso_date
from warcio.statusandheaders import StatusAndHeaders
from warcio.recordloader import ArcWarcRecord


# ============================================================================
class WARCFormat(object):
    REVISIT_PROFILE = 'http://netpreserve.org/warc/1.0/revisit/identical-payload-digest'

    WARC_VERSION = 'WARC/1.0'

    WARC_RECORDS = {'warcinfo': 'application/warc-fields',
         'response': 'application/http; msgtype=response',
         'revisit': 'application/http; msgtype=response',
         'request': 'application/http; msgtype=request',
         'metadata': 'application/warc-fields',
        }

    def __init__(self):
        self.parser = StatusAndHeadersParser([], verify=False)

    def create_warcinfo_record(self, filename, info):
        warc_headers = StatusAndHeaders(self.WARC_VERSION, [])
        warc_headers.add_header('WARC-Type', 'warcinfo')
        warc_headers.add_header('WARC-Record-ID', self._make_warc_id())
        if filename:
            warc_headers.add_header('WARC-Filename', filename)
        warc_headers.add_header('WARC-Date', self._make_warc_date())

        warcinfo = BytesIO()
        for n, v in six.iteritems(info):
            line = name + ': ' + str(value) + '\r\n'
            warcinfo.write(line.encode('latin-1'))

        length = warcinfo.tell()
        warcinfo.seek(0)

        return self.create_warc_record('', 'warcinfo',
                                       warc_headers=warc_headers,
                                       payload=warcinfo,
                                       length=length)

    def create_revisit_record(self, uri, digest, refers_to_uri, refers_to_date,
                              status_headers=None):

        record = self.create_warc_record(uri, 'revisit', status_headers=status_headers)

        record.rec_headers.add_header('WARC-Profile', self.REVISIT_PROFILE)

        record.rec_headers.add_header('WARC-Refers-To-Target-URI', refers_to_uri)
        record.rec_headers.add_header('WARC-Refers-To-Date', refers_to_date)

        record.rec_headers.add_header('WARC-Payload-Digest', digest)

        return record

    def create_warc_record(self, uri, record_type,
                           payload=None,
                           length=0,
                           warc_content_type='',
                           warc_headers_dict={},
                           warc_headers=None,
                           status_headers=None):

        if payload and not status_headers and record_type in ('response', 'request', 'revisit'):
            status_headers = self.parser.parse(payload)
            length -= payload.tell()

        if not payload:
            payload = BytesIO()
            length = 0

        if not warc_content_type:
            warc_content_type = self.WARC_RECORDS.get(record_type)

        if not warc_headers:
            warc_headers = self._init_warc_headers(uri, record_type, warc_content_type, warc_headers_dict)

        record = ArcWarcRecord('warc', record_type, warc_headers, payload,
                               status_headers, warc_content_type, length)

        record.payload_length = length

        if record_type not in ('warcinfo', 'revisit'):
            self.ensure_digest(record, block=False, payload=True)

        return record

    def create_record_from_stream(self, record_stream, length):
        warc_headers = self.parser.parse(record_stream)

        return self.create_warc_record('', warc_headers.get_header('WARC-Type'),
                                       payload=record_stream,
                                       length=length,
                                       warc_headers=warc_headers)

    @classmethod
    def _init_warc_headers(self, uri, content_type, record_type, warc_headers_dict):
        warc_headers = StatusAndHeaders(self.WARC_VERSION, list(warc_headers_dict.items()))
        warc_headers.replace_header('WARC-Type', record_type)
        if not warc_headers.get_header('WARC-Record-ID'):
            warc_headers.add_header('WARC-Record-ID', self._make_warc_id())

        if uri:
            warc_headers.replace_header('WARC-Target-URI', uri)

        if not warc_headers.get_header('WARC-Date'):
            warc_headers.add_header('WARC-Date', self._make_warc_date())

        warc_headers.add_header('Content-Type', content_type)
        return warc_headers

    @classmethod
    def _make_warc_id(self, id_=None):
        if not id_:
            id_ = uuid.uuid1()
        return '<urn:uuid:{0}>'.format(id_)

    @classmethod
    def _make_warc_date(self):
        return datetime_to_iso_date(datetime.utcnow())


