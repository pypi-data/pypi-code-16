import datetime

import mock
import pytest
import six
from six.moves.urllib.request import Request

import fedfind.const
import fedfind.helpers

# config decorators
net = pytest.mark.net

URL = 'https://dl.fedoraproject.org'
RSYNCURL = 'rsync://dl.fedoraproject.org'
COLLECTIONS_JSON = {
  "collections": [
    {
      "allow_retire": True,
      "branchname": "master",
      "date_created": "2014-05-14 12:36:15",
      "date_updated": "2016-02-23 22:56:34",
      "dist_tag": ".fc25",
      "koji_name": "rawhide",
      "name": "Fedora",
      "status": "Under Development",
      "version": "devel"
    },
    {
      "allow_retire": False,
      "branchname": "f22",
      "date_created": "2015-02-10 14:00:01",
      "date_updated": "2015-02-10 14:00:01",
      "dist_tag": ".fc22",
      "koji_name": "f22",
      "name": "Fedora",
      "status": "Active",
      "version": "22"
    },
    {
      "allow_retire": False,
      "branchname": "f23",
      "date_created": "2015-07-14 18:13:12",
      "date_updated": "2015-07-14 18:13:12",
      "dist_tag": ".fc23",
      "koji_name": "f23",
      "name": "Fedora",
      "status": "Active",
      "version": "23"
    },
    {
      "allow_retire": True,
      "branchname": "f24",
      "date_created": "2016-02-23 22:57:55",
      "date_updated": "2016-02-25 20:39:53",
      "dist_tag": ".fc24",
      "koji_name": "f24",
      "name": "Fedora",
      "status": "Under Development",
      "version": "24"
    }
  ],
  "output": "ok"
}
PDC_JSON = {
    "results": ['some', 'results'],
    "next": False
}
PDC_JSON_REAL = {
    "results": [
        {
            'compose_id': 'Fedora-24-20160314.1',
            'compose_label': 'Alpha-1.1'
        }
    ],
    "next": False
}

class FakeResp(object):
    """urlopen response stub, used in test_get_size."""
    def info(self):
        return {'Content-Length': 100}

class TestHelpers:
    """Tests for the functions in helpers.py."""
    def test_date_check(self):
        invalid = 'notadate'
        # this looks a bit silly, but we want the values of 'valid'
        # and 'obj' to match
        now = datetime.datetime.now()
        valid = now.strftime('%Y%m%d')
        obj = datetime.datetime.strptime(valid, '%Y%m%d')

        # Default case: checking valid obj or str should return obj
        assert fedfind.helpers.date_check(obj, out='obj') == obj
        assert fedfind.helpers.date_check(valid, out='obj') == obj
        assert fedfind.helpers.date_check(obj) == obj
        assert fedfind.helpers.date_check(valid) == obj

        # Checking valid obj or str with out='str' should return str
        assert fedfind.helpers.date_check(obj, out='str') == valid
        assert fedfind.helpers.date_check(valid, out='str') == valid

        # Checking valid with out='both' should return a tuple of both
        assert fedfind.helpers.date_check(obj, out='both') == (valid, obj)
        assert fedfind.helpers.date_check(valid, out='both') == (valid, obj)

        # Checking invalid with fail_raise=False should return False
        assert fedfind.helpers.date_check(invalid, fail_raise=False) is False

        # Checking invalid with fail_raise=True or default should
        # raise ValueError
        with pytest.raises(ValueError):
            fedfind.helpers.date_check(invalid, fail_raise=True)
        with pytest.raises(ValueError):
            fedfind.helpers.date_check(invalid)

    # we gotta patch the right thing...in fedfind.helpers we import
    # subprocess32 as subprocess if we can, so follow that here
    try:
        import subprocess32
        subpname = 'subprocess32'
    except ImportError:
        subpname = 'subprocess'

    @mock.patch('{0}.Popen.communicate'.format(subpname), return_value=(b'foobar', None))
    @mock.patch('{0}.Popen.poll'.format(subpname), return_value=0)
    def test_rsync_helper(self, fakepoll, fakecomm):
        assert fedfind.helpers.rsync_helper(['rsync://dl.fedoraproject.org']) == (0, 'foobar')
        assert fakecomm.call_count == 1
        assert fakepoll.call_count == 1

    @mock.patch('{0}.Popen.communicate'.format(subpname), return_value=(None,None))
    @mock.patch('{0}.Popen.poll'.format(subpname), return_value=0)
    def test_rsync_helper_noout(self, fakepoll, fakecomm):
        assert fedfind.helpers.rsync_helper(['rsync://dl.fedoraproject.org']) == (0, '')
        assert fakecomm.call_count == 1
        assert fakepoll.call_count == 1

    @mock.patch('time.sleep')
    @mock.patch('{0}.Popen.communicate'.format(subpname), return_value=(None,None))
    @mock.patch('{0}.Popen.poll'.format(subpname), return_value=5)
    def test_rsync_helper_busy(self, fakepoll, fakecomm, fakesleep):
        assert fedfind.helpers.rsync_helper(['rsync://dl.fedoraproject.org']) == (5, '')
        assert fakecomm.call_count == 6
        assert fakepoll.call_count == 6
        assert fakesleep.call_count == 5

    @mock.patch('fedfind.helpers.urlopen', return_value=True)
    def test_urlopen_retries_good(self, fakeopen):
        assert fedfind.helpers.urlopen_retries(URL) is True
        fakeopen.assert_called_with(URL)
        assert fakeopen.call_count == 1

    @mock.patch('fedfind.helpers.urlopen', side_effect=ValueError)
    def test_urlopen_retries_bad(self, fakeopen):
        with pytest.raises(ValueError):
            fedfind.helpers.urlopen_retries(URL)
        fakeopen.assert_called_with(URL)
        assert fakeopen.call_count == 5

    @mock.patch('fedfind.helpers.urlopen', return_value=mock.Mock(**{'read.return_value': b'{"foo": "bar"}'}))
    def test_download_json(self, fakeopen):
        assert fedfind.helpers.download_json(URL) == {'foo': 'bar'}

    @mock.patch('fedfind.helpers.urlopen')
    def test_url_exists_http_good(self, fakeopen):
        assert fedfind.helpers.url_exists(URL) is True
        fakeopen.assert_called_with(URL)

    @mock.patch('fedfind.helpers.urlopen', side_effect=ValueError('foo'))
    def test_url_exists_http_bad(self, fakeopen):
        assert fedfind.helpers.url_exists(URL) is False

    @mock.patch('fedfind.helpers.rsync_helper', return_value=(0, b''))
    def test_url_exists_rsync_good(self, fakeopen):
        assert fedfind.helpers.url_exists(RSYNCURL) is True

    @mock.patch('fedfind.helpers.rsync_helper', return_value=(23, b''))
    def test_url_exists_rsync_bad(self, fakeopen):
        assert fedfind.helpers.url_exists(RSYNCURL) is False

    @mock.patch('fedfind.helpers.rsync_helper', return_value=(5, b''))
    def test_url_exists_rsync_busy(self, fakeopen):
        with pytest.raises(IOError):
            fedfind.helpers.url_exists(RSYNCURL)

    @mock.patch('fedfind.helpers.rsync_helper', return_value=(6, b''))
    def test_url_exists_rsync_unknown(self, fakeopen):
        with pytest.raises(IOError):
            fedfind.helpers.url_exists(RSYNCURL)

    def test_url_exists_invalid(self):
        with pytest.raises(ValueError):
            fedfind.helpers.url_exists('jfohpjsph#^3#@^#')

    # we stub out the urlopen response with a fake class as
    # trying to do it with mocks gets a bit 'yo dawg'
    @mock.patch('fedfind.helpers.urlopen_retries', return_value=FakeResp())
    def test_get_size_bad(self, fakeopen):
        assert fedfind.helpers.get_size(URL) == 100

    def test_comma_list(self):
        # it splits lists on commas. it ain't rocket science.
        assert fedfind.helpers.comma_list('foo,Bar,moo') == ['foo', 'bar', 'moo']

    @mock.patch('fedfind.helpers.download_json', return_value=COLLECTIONS_JSON)
    def test_get_current_release(self, fakejson):
        assert fedfind.helpers.get_current_release() == 23
        assert fedfind.helpers.get_current_release(branched=True) == 24

    def test_create_image_dict(self):
        # important case: two-week atomic compose...
        ret = fedfind.helpers.create_image_dict('https://dl.fedoraproject.org/pub/alt/atomic/testing/23-20160313/Cloud_Atomic/x86_64/iso/Fedora-Cloud_Atomic-x86_64-23-20160313.iso')
        assert ret == {
            'path': 'https://dl.fedoraproject.org/pub/alt/atomic/testing/23-20160313/Cloud_Atomic/x86_64/iso/Fedora-Cloud_Atomic-x86_64-23-20160313.iso',
            'arch': 'x86_64',
            'format': 'iso',
            'type': 'boot',
            'subvariant': 'Atomic'}
        ret = fedfind.helpers.create_image_dict('https://dl.fedoraproject.org/pub/alt/atomic/testing/23-20160313/Docker/x86_64/Fedora-Docker-Base-23-20160313.x86_64.tar.xz')
        assert ret == {
            'path': 'https://dl.fedoraproject.org/pub/alt/atomic/testing/23-20160313/Docker/x86_64/Fedora-Docker-Base-23-20160313.x86_64.tar.xz',
            'arch': 'x86_64',
            'format': 'tar.xz',
            'type': 'docker',
            'subvariant': 'Docker_Base'}
        ret = fedfind.helpers.create_image_dict('https://dl.fedoraproject.org/pub/alt/atomic/testing/23-20160313/Cloud-Images/i386/Images/Fedora-Cloud-Base-23-20160313.i386.qcow2')
        assert ret == {
            'path': 'https://dl.fedoraproject.org/pub/alt/atomic/testing/23-20160313/Cloud-Images/i386/Images/Fedora-Cloud-Base-23-20160313.i386.qcow2',
            'arch': 'i386',
            'format': 'qcow2',
            'type': 'qcow2',
            'subvariant': 'Cloud_Base'}
        # some tricky cases
        ret = fedfind.helpers.create_image_dict('https://dl.fedoraproject.org/pub/archive/fedora/linux/core/1/i386/iso/yarrow-i386-disc1.iso')
        assert ret == {
            'path': 'https://dl.fedoraproject.org/pub/archive/fedora/linux/core/1/i386/iso/yarrow-i386-disc1.iso',
            'arch': 'i386',
            'format': 'iso',
            'type': 'cd',
            'subvariant': 'Everything'}

    @mock.patch('fedfind.helpers.download_json', return_value=PDC_JSON)
    def test_pdc_query(self, fakejson):
        assert fedfind.helpers.pdc_query('composes') == ['some', 'results']
        # first (and only) positional arg to the download_json call should be a Request
        req = fakejson.call_args[0][0]
        assert isinstance(req, Request)

    def test_find_cid(self):
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora-24-20160314.n.0/compose')
        assert res == 'Fedora-24-20160314.n.0'
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora-24-20160314.0/compose')
        assert res == 'Fedora-24-20160314.0'
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora-24-20160314.t.0/compose')
        assert res == 'Fedora-24-20160314.t.0'
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora-Rawhide-20160314.n.1/compose')
        assert res == 'Fedora-Rawhide-20160314.n.1'
        # a few 'close but no cigars' just for safety...
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora-24-20160314.t.u/compose')
        assert res == ''
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora-24-20160314/compose')
        assert res == ''
        res = fedfind.helpers.find_cid('https://foo.com/compose/Fedora/24-20160314.n.0/compose')
        assert res == ''

    def test_parse_cid(self):
        res = fedfind.helpers.parse_cid('Fedora-24-20160314.n.0')
        assert res == ('24', '20160314', 'nightly', 0)
        res = fedfind.helpers.parse_cid('Fedora-24-20160314.0')
        assert res == ('24', '20160314', 'production', 0)
        res = fedfind.helpers.parse_cid('Fedora-24-20160314.t.0')
        assert res == ('24', '20160314', 'test', 0)
        res = fedfind.helpers.parse_cid('Fedora-Rawhide-20160314.n.1')
        assert res == ('rawhide', '20160314', 'nightly', 1)

    @mock.patch('fedfind.helpers.download_json', return_value=PDC_JSON_REAL)
    def test_cid_from_label(self, fakejson):
        assert fedfind.helpers.cid_from_label('24', 'Alpha-1.1') == 'Fedora-24-20160314.1'

    @mock.patch('fedfind.helpers.download_json', return_value=PDC_JSON_REAL)
    def test_label_from_cid(self, fakejson):
        assert fedfind.helpers.label_from_cid('Fedora-24-20160314.1') == 'Alpha-1.1'
