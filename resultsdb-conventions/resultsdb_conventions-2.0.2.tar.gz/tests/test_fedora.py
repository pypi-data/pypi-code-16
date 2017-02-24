# Copyright (C) Red Hat Inc.
#
# resultsdb_conventions is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:   Adam Williamson <awilliam@redhat.com>

# these are all kinda inappropriate for pytest patterns
# pylint: disable=old-style-class, no-init, protected-access, no-self-use, unused-argument

"""Tests for the Fedora classes."""

from __future__ import unicode_literals
from __future__ import print_function

# external imports
import fedfind.release
import mock

# 'internal' imports
from resultsdb_conventions.fedora import (FedoraImageResult, FedoraBodhiResult)

# fedfind metadata dict used to avoid a round trip to get the real one.
METADATA01 = {
    "composeinfo": {
        "header": {
            "type": "productmd.composeinfo",
            "version": "1.2"
        },
        "payload": {
            "compose": {
                "date": "20170131",
                "id": "Fedora-Rawhide-20170131.n.1",
                "respin": 1,
                "type": "nightly"
            },
            "release": {
                "internal": False,
                "name": "Fedora",
                "short": "Fedora",
                "type": "ga",
                "version": "Rawhide"
            },
        },
    },
}

# fedfind image dict we use to avoid a round trip to get the real one.
FFIMG01 = {
    'variant': 'Server',
    'checksums': {'sha256': 'a7cd606a44b40a3e82cc71079f80b6928e155e112d0788e5cc80a6f3d4cbe6a3'},
    'arch': 'x86_64',
    'path': 'Server/x86_64/iso/Fedora-Server-dvd-x86_64-Rawhide-20170131.n.1.iso',
    'bootable': True,
    'size': 3009413120,
    'implant_md5': '962ec7863a78607ba4e3fc7cda01cc46',
    'mtime': 1485870969,
    'disc_count': 1,
    'format': 'iso',
    'volume_id': 'Fedora-S-dvd-x86_64-rawh',
    'subvariant': 'Server',
    'disc_number': 1,
    'type': 'dvd'
}


class TestFedora:
    """Fedora class tests."""

    @mock.patch.object(FedoraImageResult, 'ffimg', FFIMG01)
    @mock.patch.object(fedfind.release.RawhideNightly, 'metadata', METADATA01)
    def test_fedoraimage_basic(self):
        """This is just a pretty basic overall test that instantiates
        the most complex class, produces a result and checks its
        properties.
        """
        res = FedoraImageResult(
            cid='Fedora-Rawhide-20170131.n.1',
            filename='Fedora-Server-dvd-x86_64-Rawhide-20170131.n.1.iso',
            outcome='PASSED',
            tc_name='compose.some.test',
            note='note here',
            ref_url='https://www.job.link/',
            tc_url='https://www.test.case/',
            source='testsource' 
        )
        # Report to a MagicMock, so we can check create_result args
        fakeapi = mock.MagicMock()
        res.report(fakeapi)

        # basic attribute checks
        assert res.outcome == 'PASSED'
        assert res.tc_name == 'compose.some.test'
        assert res.note == 'note here'
        assert res.ref_url == 'https://www.job.link/'
        assert res.tc_url == 'https://www.test.case/'
        assert res.source == 'testsource'

        # check the testcase object
        assert res.testcase_object == {
            'name': 'compose.some.test',
            'ref_url': 'https://www.test.case/',
        }

        # check the extradata
        assert res.extradata == {
            'item': 'Fedora-Server-dvd-x86_64-Rawhide-20170131.n.1.iso',
            'meta.conventions': 'result productmd.compose fedora.compose productmd.image fedora.image',
            'productmd.compose.date': '20170131',
            'productmd.compose.id': 'Fedora-Rawhide-20170131.n.1',
            'productmd.compose.name': 'Fedora',
            'productmd.compose.short': 'Fedora',
            'productmd.compose.respin': 1,
            'productmd.compose.type': 'nightly',
            'productmd.compose.version': 'Rawhide',
            'productmd.image.arch': 'x86_64',
            'productmd.image.disc_number': '1',
            'productmd.image.format': 'iso',
            'productmd.image.subvariant': 'Server',
            'productmd.image.type': 'dvd',
            'source': 'testsource',
            'type': 'compose'
        }

        # check the groups
        assert res.groups == [
            {
                'description': 'source.testsource',
                'uuid': 'ddf8c194-5e34-50ec-b0e8-205c63b0dfc1'
            },
            {
                'description': 'compose.Fedora-Rawhide-20170131.n.1',
                'ref_url': 'https://kojipkgs.fedoraproject.org/compose/rawhide/Fedora-Rawhide-20170131.n.1/compose',
                'uuid': '8f6a8786-7b02-5ec0-9ac4-086ef3e33515'
            },
            {
                'description': 'testsource.Fedora-Rawhide-20170131.n.1',
                'uuid': 'b42e8fbf-b74a-5ee3-8d1d-e59e17220fce'
            },
            {
                'description': 'image.server.dvd.iso.x86_64.1',
                'uuid': '65b7f973-d87b-5008-a6e7-f431155b9a00'
            },
            {
                'description': 'testsource.server.dvd.iso.x86_64.1',
                'uuid': 'f5969a48-5c55-5d16-abb8-a94d54aacf22'
            }
        ]

    def test_fedorabodhi(self):
        """Check the expected properties of a FedoraBodhiResult."""
        res = FedoraBodhiResult(
            update='FEDORA-2017-e6d7184200',
            outcome='PASSED',
            tc_name='update.some.test',
            note='note here',
            ref_url='https://www.job.link/',
            tc_url='https://www.test.case/',
            source='testsource'
        )
        # Report to a MagicMock, so we can check create_result args
        fakeapi = mock.MagicMock()
        res.report(fakeapi)

        # basic attribute checks
        assert res.outcome == 'PASSED'
        assert res.tc_name == 'update.some.test'
        assert res.note == 'note here'
        assert res.ref_url == 'https://www.job.link/'
        assert res.tc_url == 'https://www.test.case/'
        assert res.source == 'testsource'

        # check the testcase object
        assert res.testcase_object == {
            'name': 'update.some.test',
            'ref_url': 'https://www.test.case/',
        }

        # check the extradata
        assert res.extradata == {
            'item': 'FEDORA-2017-e6d7184200',
            'meta.conventions': 'result fedora.bodhi',
            'source': 'testsource',
            'type': 'bodhi_update'
        }

        # check the groups
        assert res.groups == [
            {
                'description': 'source.testsource',
                'uuid': 'ddf8c194-5e34-50ec-b0e8-205c63b0dfc1'
            },
            {
                'description': 'bodhi.FEDORA-2017-e6d7184200',
                'ref_url': 'https://bodhi.fedoraproject.org/updates/FEDORA-2017-e6d7184200',
                'uuid': 'c67605d5-0ff7-5f1e-91df-3d2ad094c902'
            },
            {
                'description': 'testsource.FEDORA-2017-e6d7184200',
                'uuid': 'd02731e7-46d3-545b-b355-3ff01ff62de1'
            },
        ]

# vim: set textwidth=120 ts=8 et sw=4:
