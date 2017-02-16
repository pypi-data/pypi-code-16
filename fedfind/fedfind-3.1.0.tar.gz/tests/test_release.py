# Copyright (C) 2015 Red Hat
#
# This file is part of fedfind.
#
# fedfind is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

"""Tests for release.py."""

from __future__ import unicode_literals
from __future__ import print_function

import codecs
import datetime
import json
import os
import pytest

import mock
import fedfind.release

# Some chunks of HTML from mirror package directories for testing
# get_package_nvras. FC6 has generic release (no fcXX), F16 has
# fcXX, F21 is split by initials. FC6 is from a mirror, F18 and F21
# are from dl.fp.o.

FC6PACKAGEHTML = """
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
<title>Index of /fedora/archive/fedora/linux/core/6/source/SRPMS/</title>
<style type="text/css">
a, a:active {text-decoration: none; color: blue;}
a:visited {color: #48468F;}
a:hover, a:focus {text-decoration: underline; color: red;}
body {background-color: #F5F5F5;}
h2 {margin-bottom: 12px;}
table {margin-left: 12px;}
th, td { font: 90% monospace; text-align: left;}
th { font-weight: bold; padding-right: 14px; padding-bottom: 3px;}
td {padding-right: 14px;}
td.s, th.s {text-align: right;}
div.list { background-color: white; border-top: 1px solid #646464; border-bottom: 1px solid #646464; padding-top: 10px; padding-bottom: 14px;}
div.foot { font: 90% monospace; color: #787878; padding-top: 4px;}
</style>
</head>
<body>
<h2>Index of /fedora/archive/fedora/linux/core/6/source/SRPMS/</h2>
<div class="list">
<table summary="Directory Listing" cellpadding="0" cellspacing="0">
<thead><tr><th class="n">Name</th><th class="m">Last Modified</th><th class="s">Size</th><th class="t">Type</th></tr></thead>
<tbody>
<tr><td class="n"><a href="../">Parent Directory</a>/</td><td class="m">&nbsp;</td><td class="s">- &nbsp;</td><td class="t">Directory</td></tr>
<tr><td class="n"><a href="repodata/">repodata</a>/</td><td class="m">2006-Oct-17 21:22:24</td><td class="s">- &nbsp;</td><td class="t">Directory</td></tr>
<tr><td class="n"><a href="am-utils-6.1.5-4.src.rpm">am-utils-6.1.5-4.src.rpm</a></td><td class="m">2006-Oct-05 17:06:36</td><td class="s">1.8M</td><td class="t">application/x-rpm</td></tr>
<tr><td class="n"><a href="amanda-2.5.0p2-4.src.rpm">amanda-2.5.0p2-4.src.rpm</a></td><td class="m">2006-Oct-05 14:53:24</td><td class="s">1.7M</td><td class="t">application/x-rpm</td></tr>
<tr><td class="n"><a href="amtu-1.0.4-3.1.src.rpm">amtu-1.0.4-3.1.src.rpm</a></td><td class="m">2006-Oct-05 15:01:09</td><td class="s">58.9K</td><td class="t">application/x-rpm</td></tr>
<tr><td class="n"><a href="anaconda-11.1.1.3-1.src.rpm">anaconda-11.1.1.3-1.src.rpm</a></td><td class="m">2006-Oct-17 19:46:31</td><td class="s">3.7M</td><td class="t">application/x-rpm</td></tr>
<tr><td class="n"><a href="anacron-2.3-41.fc6.src.rpm">anacron-2.3-41.fc6.src.rpm</a></td><td class="m">2006-Oct-12 23:23:17</td><td class="s">42.0K</td><td class="t">application/x-rpm</td></tr>
<tr><td class="n"><a href="ant-1.6.5-2jpp.2.src.rpm">ant-1.6.5-2jpp.2.src.rpm</a></td><td class="m">2006-Oct-05 16:00:10</td><td class="s">5.0M</td><td class="t">application/x-rpm</td></tr>
<tr><td class="n"><a href="anthy-7900-2.fc6.src.rpm">anthy-7900-2.fc6.src.rpm</a></td><td class="m">2006-Oct-05 17:13:24</td><td class="s">4.4M</td><td class="t">application/x-rpm</td></tr>
<tr><td class="n"><a href="antlr-2.7.6-4jpp.2.src.rpm">antlr-2.7.6-4jpp.2.src.rpm</a></td><td class="m">2006-Oct-05 14:54:40</td><td class="s">1.3M</td><td class="t">application/x-rpm</td></tr>
<tr><td class="n"><a href="apmd-3.2.2-5.src.rpm">apmd-3.2.2-5.src.rpm</a></td><td class="m">2006-Oct-05 17:06:38</td><td class="s">99.6K</td><td class="t">application/x-rpm</td></tr>
<tr><td class="n"><a href="apr-1.2.7-10.src.rpm">apr-1.2.7-10.src.rpm</a></td><td class="m">2006-Oct-05 17:04:36</td><td class="s">1.0M</td><td class="t">application/x-rpm</td></tr>
<tr><td class="n"><a href="basesystem-8.0-5.1.1.src.rpm">basesystem-8.0-5.1.1.src.rpm</a></td><td class="m">2006-Oct-05 14:53:05</td><td class="s">3.7K</td><td class="t">application/x-rpm</td></tr>
<tr><td class="n"><a href="bash-3.1-16.1.src.rpm">bash-3.1-16.1.src.rpm</a></td><td class="m">2006-Oct-05 17:08:36</td><td class="s">4.4M</td><td class="t">application/x-rpm</td></tr>
<tr><td class="n"><a href="bc-1.06-21.src.rpm">bc-1.06-21.src.rpm</a></td><td class="m">2006-Oct-05 18:46:45</td><td class="s">236.9K</td><td class="t">application/x-rpm</td></tr>
"""

F16PACKAGEHTML = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of /pub/archive/fedora/linux/releases/16/Everything/source/SRPMS</title>
 </head>
 <body>
<h1>Index of /pub/archive/fedora/linux/releases/16/Everything/source/SRPMS</h1>
<pre><img src="/icons/blank.gif" alt="Icon "> <a href="?C=N;O=D">Name</a>                                                                         <a href="?C=M;O=A">Last modified</a>      <a href="?C=S;O=A">Size</a>  <a href="?C=D;O=A">Description</a><hr><img src="/icons/back.gif" alt="[PARENTDIR]"> <a href="/pub/archive/fedora/linux/releases/16/Everything/source/">Parent Directory</a>                                                                                  -   
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amanda-3.3.0-2.fc16.src.rpm">amanda-3.3.0-2.fc16.src.rpm</a>                                                  2011-07-30 03:39  4.0M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amanith-0.3-17.fc16.src.rpm">amanith-0.3-17.fc16.src.rpm</a>                                                  2011-07-30 03:18  7.3M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amarok-2.4.3-1.fc16.src.rpm">amarok-2.4.3-1.fc16.src.rpm</a>                                                  2011-08-02 02:53   17M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amavisd-new-2.6.6-1.fc16.src.rpm">amavisd-new-2.6.6-1.fc16.src.rpm</a>                                             2011-09-19 17:12  950K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amide-1.0.0-1.fc16.src.rpm">amide-1.0.0-1.fc16.src.rpm</a>                                                   2011-10-11 00:33  1.5M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amoebax-0.2.0-7.fc15.src.rpm">amoebax-0.2.0-7.fc15.src.rpm</a>                                                 2011-07-30 01:29   10M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amora-1.1-6.fc15.src.rpm">amora-1.1-6.fc15.src.rpm</a>                                                     2011-07-30 02:16  161K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amqp-1.0.819819-2.fc15.src.rpm">amqp-1.0.819819-2.fc15.src.rpm</a>                                               2011-07-30 03:46  225K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amsn-0.98.4-4.fc16.src.rpm">amsn-0.98.4-4.fc16.src.rpm</a>                                                   2011-07-30 04:03   13M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amtterm-1.3-1.fc16.src.rpm">amtterm-1.3-1.fc16.src.rpm</a>                                                   2011-07-30 03:51   43K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amtu-1.0.8-8.fc15.src.rpm">amtu-1.0.8-8.fc15.src.rpm</a>                                                    2011-07-30 05:09  142K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="anaconda-16.25-1.fc16.src.rpm">anaconda-16.25-1.fc16.src.rpm</a>                                                2011-11-03 02:14  5.1M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="anaconda-yum-plugins-1.0-6.fc15.src.rpm">anaconda-yum-plugins-1.0-6.fc15.src.rpm</a>                                      2011-07-30 02:19   14K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="basesystem-10.0-5.fc16.src.rpm">basesystem-10.0-5.fc16.src.rpm</a>                                               2011-07-30 02:47  5.7K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="bash-4.2.10-4.fc16.src.rpm">bash-4.2.10-4.fc16.src.rpm</a>                                                   2011-07-30 04:23  6.7M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="bash-completion-1.3-6.fc16.src.rpm">bash-completion-1.3-6.fc16.src.rpm</a>                                           2011-09-06 16:43  233K  
<hr></pre>
"""

F18PACKAGEHTMLA = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of /pub/archive/fedora/linux/releases/18/Everything/source/SRPMS/a</title>
 </head>
 <body>
<h1>Index of /pub/archive/fedora/linux/releases/18/Everything/source/SRPMS/a</h1>
<pre><img src="/icons/blank.gif" alt="Icon "> <a href="?C=N;O=D">Name</a>                                                           <a href="?C=M;O=A">Last modified</a>      <a href="?C=S;O=A">Size</a>  <a href="?C=D;O=A">Description</a><hr><img src="/icons/back.gif" alt="[PARENTDIR]"> <a href="/pub/archive/fedora/linux/releases/18/Everything/source/SRPMS/">Parent Directory</a>                                                                    -   
<img src="/icons/unknown.gif" alt="[   ]"> <a href="am-utils-6.1.5-23.fc18.src.rpm">am-utils-6.1.5-23.fc18.src.rpm</a>                                 2012-08-11 04:16  1.9M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amanda-3.3.2-2.fc18.src.rpm">amanda-3.3.2-2.fc18.src.rpm</a>                                    2012-09-18 17:58  4.2M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amanith-0.3-22.fc18.src.rpm">amanith-0.3-22.fc18.src.rpm</a>                                    2012-08-11 04:50  7.3M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amarok-2.6.0-4.fc18.src.rpm">amarok-2.6.0-4.fc18.src.rpm</a>                                    2012-09-12 18:15   40M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amavisd-new-2.8.0-2.fc18.src.rpm">amavisd-new-2.8.0-2.fc18.src.rpm</a>                               2012-08-11 06:33  1.0M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="ambdec-0.5.1-3.fc18.src.rpm">ambdec-0.5.1-3.fc18.src.rpm</a>                                    2012-08-11 06:47  225K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amide-1.0.0-3.fc18.src.rpm">amide-1.0.0-3.fc18.src.rpm</a>                                     2012-08-11 04:36  1.5M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amoebax-0.2.0-10.fc18.src.rpm">amoebax-0.2.0-10.fc18.src.rpm</a>                                  2012-08-11 04:41   10M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amora-1.1-9.fc18.src.rpm">amora-1.1-9.fc18.src.rpm</a>                                       2012-11-02 03:48  161K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amqp-1.0.819819-4.fc18.src.rpm">amqp-1.0.819819-4.fc18.src.rpm</a>                                 2012-08-11 07:05  225K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="ams-2.0.1-5.fc18.src.rpm">ams-2.0.1-5.fc18.src.rpm</a>                                       2012-10-26 06:52  291K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amsn-0.98.9-4.fc18.src.rpm">amsn-0.98.9-4.fc18.src.rpm</a>                                     2012-08-11 07:22   13M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amtterm-1.3-4.fc18.src.rpm">amtterm-1.3-4.fc18.src.rpm</a>                                     2012-08-11 05:06   44K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="amtu-1.0.8-12.fc18.src.rpm">amtu-1.0.8-12.fc18.src.rpm</a>                                     2012-08-11 04:53  143K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="anaconda-18.37.11-1.fc18.src.rpm">anaconda-18.37.11-1.fc18.src.rpm</a>                               2013-01-08 04:12  3.7M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="anaconda-yum-plugins-1.0-8.fc18.src.rpm">anaconda-yum-plugins-1.0-8.fc18.src.rpm</a>                        2012-08-11 04:20   14K  
"""

F18PACKAGEHTMLB = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of /pub/archive/fedora/linux/releases/18/Everything/source/SRPMS/b</title>
 </head>
 <body>
<h1>Index of /pub/archive/fedora/linux/releases/18/Everything/source/SRPMS/b</h1>
<pre><img src="/icons/blank.gif" alt="Icon "> <a href="?C=N;O=D">Name</a>                                                           <a href="?C=M;O=A">Last modified</a>      <a href="?C=S;O=A">Size</a>  <a href="?C=D;O=A">Description</a><hr><img src="/icons/back.gif" alt="[PARENTDIR]"> <a href="/pub/archive/fedora/linux/releases/18/Everything/source/SRPMS/">Parent Directory</a>                                                                    -   
<img src="/icons/unknown.gif" alt="[   ]"> <a href="basesystem-10.0-7.fc18.src.rpm">basesystem-10.0-7.fc18.src.rpm</a>                                 2012-08-11 05:28  6.0K  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="bash-4.2.39-3.fc18.src.rpm">bash-4.2.39-3.fc18.src.rpm</a>                                     2012-11-30 03:56  6.8M  
<img src="/icons/unknown.gif" alt="[   ]"> <a href="bash-completion-2.0-2.fc18.src.rpm">bash-completion-2.0-2.fc18.src.rpm</a>
"""

# Fake PDC response for get_package_nvras testing.

PDCPACKAGES = [
        {
            "id": 222481,
            "name": "anaconda",
            "version": "24.13",
            "epoch": 0,
            "release": "1.fc24",
            "arch": "src",
            "srpm_name": "anaconda",
            "srpm_nevra": "anaconda-0:24.13-1.fc24.src",
            "filename": "anaconda-24.13-1.fc24.src.rpm",
        },
        {
            "id": 120399,
            "name": "bash",
            "version": "4.3.42",
            "epoch": 0,
            "release": "4.fc24",
            "arch": "src",
            "srpm_name": "bash",
            "srpm_nevra": "bash-0:4.3.42-4.fc24.src",
            "filename": "bash-4.3.42-4.fc24.src.rpm",
        },
        {
            "id": 222118,
            "name": "amanda",
            "version": "3.3.8",
            "epoch": 0,
            "release": "1.fc24",
            "arch": "src",
            "srpm_name": "amanda",
            "srpm_nevra": "amanda-0:3.3.8-1.fc24.src",
            "filename": "amanda-3.3.8-1.fc24.src.rpm",
        }
]


class FakeRelease(object):
    """Release stub used for testing nightly respin guessing. Gives
    the magic 'good' values for exists and status if respin is 3.
    """
    def __init__(self, respin='', *args, **kwargs):
        self.exists = False
        self.status = 'DOOMED'
        self.respin = respin
        if respin == 3:
            self.exists = True
            self.status = 'FINISHED'


class FakeReleaseExists(object):
    """A fake release which always exists."""
    def __init__(self, *args, **kwargs):
        self.exists = True
        self.status = 'FINISHED'


class FakeReleaseNotExists(object):
    """A fake release which never exists."""
    def __init__(self, *args, **kwargs):
        self.exists = False
        self.status = 'DOOMED'


class FakeResponsePackages(object):
    """urlopen response stub used for get_package_nvr testing."""
    def __init__(self, url):
        self.url = url

    def read(self):
        """Returns the appropriate chunk of HTML (see above) if the
        correct URL was given.
        """
        if self.url == 'https://download.fedoraproject.org/pub/archive/fedora/linux/core/1/SRPMS/':
            # we just pretend 1 is 6, it's easier
            return FC6PACKAGEHTML
        elif self.url == 'https://download.fedoraproject.org/pub/archive/fedora/linux/core/6/source/SRPMS/':
            return FC6PACKAGEHTML
        elif self.url == 'https://download.fedoraproject.org/pub/archive/fedora/linux/releases/16/Everything/source/SRPMS/':
            return F16PACKAGEHTML
        elif self.url == 'https://download.fedoraproject.org/pub/archive/fedora/linux/releases/18/Everything/source/SRPMS/a/':
            return F18PACKAGEHTMLA
        elif self.url == 'https://download.fedoraproject.org/pub/archive/fedora/linux/releases/18/Everything/source/SRPMS/b/':
            return F18PACKAGEHTMLB
        elif self.url == 'https://download.fedoraproject.org/pub/archive/fedora/linux/releases/18/Everything/source/SRPMS/f/':
            return ""
        elif self.url == 'https://kojipkgs.fedoraproject.org/compose/branched/Fedora-24-20160321.n.0/compose/Everything/source/tree/Packages/a/':
            return F18PACKAGEHTMLA
        elif self.url == 'https://kojipkgs.fedoraproject.org/compose/branched/Fedora-24-20160321.n.0/compose/Everything/source/tree/Packages/b/':
            return F18PACKAGEHTMLB
        elif self.url == 'https://kojipkgs.fedoraproject.org/compose/branched/Fedora-24-20160321.n.0/compose/Everything/source/tree/Packages/f/':
            return ""
        else:
            raise ValueError("URL {0} not expected!".format(self.url))

def urlopen_fake_package(url):
    """Stub for urlopen_retries which returns FakeResponsePackages."""
    return FakeResponsePackages(url)

class TestRelease:
    """Tests for release.py."""

    def test_get_release_simple(self):
        """Tests for get_release that require no online guessing or
        checking, hence no mocking.
        """
        datestr = datetime.date.today().strftime('%Y%m%d')
        rels = (
            # Archive stable.
            ((15, '', '', None), (fedfind.release.ArchiveRelease, '15')),
            # Fedora Core stable (release string).
            (('6', '', '', None), (fedfind.release.CoreRelease, '6')),
            # 'Final' treated as stable.
            (('6', 'Final', '', None), (fedfind.release.CoreRelease, '6')),
            # Milestone.
            ((23, 'Beta', '', None), (fedfind.release.Milestone, '23', 'Beta')),
            # Branched nightly.
            ((23, 'Branched', datestr, 1), (fedfind.release.BranchedNightly, '23', 'Branched', datestr, '1')),
            # Rawhide nightly.
            (('Rawhide', '', datestr, 2), (fedfind.release.RawhideNightly, 'Rawhide', '', datestr, '2')),
            # Atomic nightly.
            ((24, 'Atomic', datestr, 0), (fedfind.release.AtomicNightly, '24', 'Atomic', datestr, '0')),
            # Wikitcms format Rawhide.
            (('24', 'Rawhide', '{0}.n.0'.format(datestr), None),
             (fedfind.release.RawhideNightly, 'Rawhide', '', datestr, '0')),
            # OFFLINE GUESSES
            # Date guesses.
            ((23, 'Branched', '', 0), (fedfind.release.BranchedNightly, '23', 'Branched', datestr, '0')),
            (('Rawhide', '', '', 0), (fedfind.release.RawhideNightly, 'Rawhide', '', datestr, '0')),
            ((24, 'Atomic', '', 0), (fedfind.release.AtomicNightly, '24', 'Atomic', datestr, '0')),
            # Default, check None is handled.
            ((None, None, None, 0), (fedfind.release.RawhideNightly, 'Rawhide', '', datestr, '0')),
        )

        # Test that various get_release() invocations return expected
        # classes and values. Each rel's first tuple is the release,
        # milestone, compose values to pass to get_release. Its second
        # tuple's first value is always the expected class. The next
        # three values of the second tuple are optional, and they are
        # the expected release, milestone and compose; each will be
        # checked if present.
        for ((release, milestone, compose, respin), expected) in rels:
            got = fedfind.release.get_release(release, milestone, compose, respin)
            if not isinstance(got, expected[0]):
                pytest.fail("Testing {0} {1} {2} got class {3}".format(
                    release, milestone, compose, got.__class__))
            if len(expected) > 1:
                if not got.release == expected[1]:
                    pytest.fail("Testing {0} {1} {2} got release {3}".format(
                        release, milestone, compose, got.release))
            if len(expected) > 2:
                if not got.milestone == expected[2]:
                    pytest.fail("Testing {0} {1} {2} got milestone {3}".format(
                        release, milestone, compose, got.milestone))
            if len(expected) > 3:
                if not got.compose == expected[3]:
                    pytest.fail("Testing {0} {1} {2} got compose {3}".format(
                        release, milestone, compose, got.compose))
            if len(expected) > 4:
                if not got.respin == expected[4]:
                    pytest.fail("Testing {0} {1} {2} {3} got respin {4}".format(
                        release, milestone, compose, respin, got.respin))

        # Sanity check tests.
        with pytest.raises(ValueError):
            fedfind.release.get_release('foobar')

        with pytest.raises(ValueError):
            fedfind.release.get_release('23', '', 'RC2')

    @mock.patch('fedfind.release.Production.label', 'Alpha-1.1')
    def test_get_release_production(self):
        """Explicitly getting a Production (i.e. a production compose
        on kojipkgs, not mirrored to alt, which is a Compose). This
        is the same path hit if get_release is called with a compose
        ID for a production compose, and promote is not set True.
        """
        ret = fedfind.release.get_release(24, 'Production', '20160314', 0)
        assert isinstance(ret, fedfind.release.Production)
        assert ret.release == '24'
        assert ret.milestone == 'Alpha'
        assert ret.compose == '1'
        assert ret.respin == '1'

    @mock.patch('fedfind.helpers.label_from_cid', return_value="Alpha-1.1")
    @mock.patch('fedfind.release.Compose.exists', True)
    def test_get_release_cid_promote(self, fakelab):
        """Requesting release from a production compose ID with
        promote set to True should return a Compose if possible.
        """
        ret = fedfind.release.get_release(cid='Fedora-24-20160314.0', promote=True)
        assert isinstance(ret, fedfind.release.Compose)
        assert ret.release == '24'
        assert ret.milestone == 'Alpha'
        assert ret.compose == '1'
        assert ret.respin == '1'
        fakelab.assert_called_with('Fedora-24-20160314.0')

    @mock.patch('fedfind.helpers.label_from_cid', return_value="Alpha-1.1")
    @mock.patch('fedfind.helpers.cid_from_label')
    @mock.patch('fedfind.release.Compose.exists', False)
    def test_get_release_cid_promote_fail(self, fakecid, fakelab):
        """This tests a rather snaky path: we call get_release with
        a CID and promote=True; the specified compose has a label, so
        we try and get a Compose, but the compose is not mirrored, so
        we fail. In this case we should fall back on a Production *and
        not waste time on a remote trip to recreate the CID*, instead
        it should be reused.
        """
        ret = fedfind.release.get_release(cid='Fedora-24-20160314.0', promote=True)
        assert isinstance(ret, fedfind.release.Production)
        fakelab.assert_called_with('Fedora-24-20160314.0')
        assert fakecid.call_count == 0

    def test_get_release_cid_atomic_new(self):
        """Test that new (Pungi 4) 2 Week Atomic compose IDs are
        handled. They have 'Fedora-Atomic' as the product name instead
        of 'Fedora'.
        """
        ret = fedfind.release.get_release(cid='Fedora-Atomic-24-20160628.1')
        assert isinstance(ret, fedfind.release.AtomicNightly)
        assert ret.release == '24'
        assert ret.compose == '20160628'
        assert ret.respin == '1'

    @mock.patch('fedfind.release.Compose.exists', True)
    def test_get_release_compose(self):
        """A production/candidate compose. This tests the case where
        the compose is found on the mirror system. Also tests that
        'Final' is converted to 'RC'.
        """
        ret = fedfind.release.get_release(24, 'Final', 1, 1)
        assert isinstance(ret, fedfind.release.Compose)
        assert ret.release == '24'
        assert ret.milestone == 'RC'
        assert ret.compose == '1'
        assert ret.respin == '1'
        assert ret.label == 'RC-1.1'

    @mock.patch('fedfind.helpers.cid_from_label', return_value='Fedora-24-20160316.3')
    @mock.patch('fedfind.release.Compose.exists', False)
    def test_get_release_compose_fallback(self, fakecid):
        """A production/candidate compose. This tests the case where
        the compose is not found on the mirror system so we fall back
        on finding the compose ID and returning a Production.
        """
        ret = fedfind.release.get_release(24, 'Alpha', 1, 5)
        assert isinstance(ret, fedfind.release.Production)
        fakecid.assert_called_with(24, 'Alpha-1.5')

    @mock.patch('fedfind.release.ArchiveRelease.exists', False)
    def test_get_stable_current(self):
        ret = fedfind.release.get_release(23)
        assert isinstance(ret, fedfind.release.CurrentRelease)
        assert ret.release == '23'

    @mock.patch('fedfind.release.ArchiveRelease.exists', True)
    def test_get_stable_archive(self):
        # NOTE: this test is intended to hit the code which checks
        # whether an ArchiveRelease exists and returns it if so; the
        # tested number has to be greater than the cutoff which just
        # returns an ArchiveRelease without checking
        ret = fedfind.release.get_release(23)
        assert isinstance(ret, fedfind.release.ArchiveRelease)
        assert ret.release == '23'

    @mock.patch('fedfind.helpers.get_current_release', return_value=23)
    def test_get_release_guess_release(self, fakecurrent):
        # Release guessing. We can't test this very hard or we'd have
        # to keep updating the tests all the goddamned time, or the
        # test would duplicate the logic of get_current_release and
        # that seems pointless. But we can at least check it's not
        # crashing and returns the right class.
        datestr = datetime.date.today().strftime('%Y%m%d')

        got = fedfind.release.get_release('', 'Branched', '', 0)
        assert isinstance(got, fedfind.release.BranchedNightly)
        assert got.compose == datestr
        assert got.release == '24'

        got = fedfind.release.get_release('', 'Atomic', '', 0)
        assert isinstance(got, fedfind.release.AtomicNightly)
        assert got.compose == datestr
        assert got.release == '23'

    @mock.patch('fedfind.release.RawhideNightly', FakeRelease)
    @mock.patch('fedfind.release.BranchedNightly', FakeRelease)
    @mock.patch('fedfind.release.AtomicNightly', FakeRelease)
    def test_get_release_guess_respin(self):
        got = fedfind.release.get_release(24, 'Branched', '20160314')
        assert isinstance(got, fedfind.release.BranchedNightly)
        assert got.respin == 3
        got = fedfind.release.get_release('Rawhide', '', '20160314')
        assert isinstance(got, fedfind.release.RawhideNightly)
        assert got.respin == 3
        got = fedfind.release.get_release(24, 'Atomic', '20160628')
        assert isinstance(got, fedfind.release.AtomicNightly)
        assert got.respin == 3

    @mock.patch('fedfind.release.BranchedNightly', FakeReleaseExists)
    @mock.patch('fedfind.release.AtomicNightly', FakeReleaseExists)
    def test_get_release_guess_nightly_branched_exists(self):
        """Test nightly type guessing: if we specify a date and a
        release number, but no milestone, fedfind should guess between
        BranchedNightly and AtomicNightly. If Branched exists, we
        should return it.
        """
        got = fedfind.release.get_release(25, '', '20161006')
        assert isinstance(got, fedfind.release.BranchedNightly)
        got = fedfind.release.get_release(25, '', '20161006', 3)
        assert isinstance(got, fedfind.release.BranchedNightly)

    @mock.patch('fedfind.release.BranchedNightly', FakeReleaseNotExists)
    @mock.patch('fedfind.release.AtomicNightly', FakeReleaseExists)
    def test_get_release_guess_nightly_branched_exists(self):
        """Test nightly type guessing: if we specify a date and a
        release number, but no milestone, fedfind should guess between
        BranchedNightly and AtomicNightly. If Branched doesn't exist
        but Atomic does, we should return Atomic.
        """
        got = fedfind.release.get_release(25, '', '20161006')
        assert isinstance(got, fedfind.release.AtomicNightly)
        got = fedfind.release.get_release(25, '', '20161006', 3)
        assert isinstance(got, fedfind.release.AtomicNightly)

    @mock.patch('fedfind.release.BranchedNightly', FakeReleaseNotExists)
    @mock.patch('fedfind.release.AtomicNightly', FakeReleaseNotExists)
    def test_get_release_guess_nightly_branched_exists(self):
        """Test nightly type guessing: if we specify a date and a
        release number, but no milestone, fedfind should guess between
        BranchedNightly and AtomicNightly. If neither exists, we should
        return Branched.
        """
        got = fedfind.release.get_release(25, '', '20161006')
        assert isinstance(got, fedfind.release.BranchedNightly)
        got = fedfind.release.get_release(25, '', '20161006', 3)
        assert isinstance(got, fedfind.release.BranchedNightly)

    @mock.patch('fedfind.helpers.urlopen_retries', urlopen_fake_package)
    def test_get_package_nvras_fc1(self):
        """FC1: no /Everything, no /source, no split-by-initials."""
        rel = fedfind.release.get_release(1)
        pkgs = rel.get_package_nvras(['amanda', 'anaconda', 'bash', 'fakepackage'])
        assert pkgs == {
            'amanda': 'amanda-2.5.0p2-4.src',
            'anaconda': 'anaconda-11.1.1.3-1.src',
            'bash': 'bash-3.1-16.1.src',
            'fakepackage': ''
        }

    @mock.patch('fedfind.helpers.urlopen_retries', urlopen_fake_package)
    def test_get_package_nvras_fc6(self):
        """FC6: Still no /Everything, /source appeared, no
        split-by-initials.
        """
        rel = fedfind.release.get_release(6)
        pkgs = rel.get_package_nvras(['amanda', 'anaconda', 'bash', 'fakepackage'])
        assert pkgs == {
            'amanda': 'amanda-2.5.0p2-4.src',
            'anaconda': 'anaconda-11.1.1.3-1.src',
            'bash': 'bash-3.1-16.1.src',
            'fakepackage': ''
        }

    @mock.patch('fedfind.helpers.urlopen_retries', urlopen_fake_package)
    def test_get_package_nvras_f16(self):
        """F16: /Everything showed up, still no split-by-initials."""
        rel = fedfind.release.get_release(16)
        pkgs = rel.get_package_nvras(['amanda', 'anaconda', 'bash', 'fakepackage'])
        assert pkgs == {
            'amanda': 'amanda-3.3.0-2.fc16.src',
            'anaconda': 'anaconda-16.25-1.fc16.src',
            'bash': 'bash-4.2.10-4.fc16.src',
            'fakepackage': ''
        }

    @mock.patch('fedfind.helpers.urlopen_retries', urlopen_fake_package)
    def test_get_package_nvras_f18(self):
        """F18: split-by-initials now in effect."""
        rel = fedfind.release.get_release(18)
        pkgs = rel.get_package_nvras(['amanda', 'anaconda', 'bash', 'fakepackage'])
        assert pkgs == {
            'amanda': 'amanda-3.3.2-2.fc18.src',
            'anaconda': 'anaconda-18.37.11-1.fc18.src',
            'bash': 'bash-4.2.39-3.fc18.src',
            'fakepackage': ''
        }

    def test_all_stable(self, http, clean_home, pdc):
        """Test that we get the expected image dicts for all stable
        releases, using the test HTTP server and home directory and
        the PDC query mock. Also check there are no missing expected
        images (as a test for check_expected).
        """
        ref = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'allstable.json')
        with codecs.open(ref, encoding='utf-8') as reffh:
            expected = json.loads(reffh.read())
        for relnum in expected:
            rel = fedfind.release.get_release(relnum)
            imgs = sorted(rel.all_images, key=lambda x:x['path'])
            assert expected[relnum] == imgs
            # we have to force the release to 'exist' or else
            # check_expected bails
            rel._exists = True
            assert not rel.check_expected()

    # FIXME: Pungi 4 PDC-based get_pkg_nvras method is temporarily
    # disabled due to
    # https://github.com/fedora-infra/pdc-updater/issues/10 so this
    # is using the same mirror-scrape-y method for now. Pungi 4
    # composes have a different layout again under /Everything, we
    # use the same mock values as F18.
    #@mock.patch('fedfind.helpers.pdc_query', return_value=PDCPACKAGES)
    @mock.patch('fedfind.helpers.urlopen_retries', urlopen_fake_package)
    @mock.patch('fedfind.release.BranchedNightly.cid', "Fedora-24-20160321.n.0")
#    def test_get_package_nvras_pungi4(self, fakepdc):
    def test_get_package_nvras_pungi4(self):
        """Pungi 4 compose: we hit PDC."""
        rel = fedfind.release.get_release(24, 'Branched', '20160321', 0)
        pkgs = rel.get_package_nvras(['amanda', 'anaconda', 'bash', 'fakepackage'])
        assert pkgs == {
            'amanda': 'amanda-3.3.2-2.fc18.src',
            'anaconda': 'anaconda-18.37.11-1.fc18.src',
            'bash': 'bash-4.2.39-3.fc18.src',
            'fakepackage': ''
#            'amanda': 'amanda-0:3.3.8-1.fc24.src',
#            'anaconda': 'anaconda-0:24.13-1.fc24.src',
#            'bash': 'bash-0:4.3.42-4.fc24.src',
        }
        #fakepdc.assert_called_with('rpms', [('compose', 'Fedora-24-20160321.n.0'), ('arch', 'src'), ('name', 'amanda'), ('name', 'anaconda'), ('name', 'bash'), ('name', 'fakepackage')])
