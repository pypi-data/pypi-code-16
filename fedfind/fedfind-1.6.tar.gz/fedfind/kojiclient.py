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

"""A subclass of xmlrpclib.ServerProxy to handle Koji interaction with
a couple of custom methods.
"""

import datetime
import itertools
import logging
import six
from six.moves import xmlrpc_client

import fedfind.const
import fedfind.exceptions
import fedfind.helpers

logger = logging.getLogger(__name__)

def taskrelpath(task_id):
    """Return the relative path for the task work directory. Stolen
    from koji.
    """
    # I prefer .format() as you can see everywhere else, but keeping
    # this identical to the Koji code for clarity.
    return "tasks/%s/%s" % (task_id % 10000, task_id)

class ClientSession(xmlrpc_client.ServerProxy):
    """Add a couple of methods to find nightly image files. We use
    the standard xmlrpclib rather than koji.ClientSession because
    we want fedfind to be usable on non-Fedora systems, and the koji
    module isn't widely available or easily deployable on non-Fedora
    systems."""
    def __init__(self, *args):
        # old-style class, can't use super()
        xmlrpc_client.ServerProxy.__init__(self, *args)

    def find_nightly_tasks(self, date=None, release=None, opts=None):
        """This is basically a wrapper around koji's listTasks() which
        will only return tasks that look like nightly image builds. If
        you pass date (as a datetime.date instance) it will find only
        nightlies from that date, by searching a window padded one day
        in either direction and then filtering down by a task request
        parameter which specifies the date. If you pass release (as a
        string, a Fedora release number or 'rawhide') it will find
        only nightlies for that release, by checking another request
        parameter. You can pass opts as a dict of query options, as
        listTasks() expects, and they will be passed through, except
        for 'decode' (which we need to be True to do the filtering),
        'createdAfter' and 'createdBefore' if you pass date (so just
        do one or the other), and 'owner' (which is hardwired to 2745,
        'masher', as the least bad way to avoid treating TC/RC builds
        with a date stamp as nightlies).

        As a SECRET FEATURE, allows opts['method'] to be an iterable.
        Handles this by using a multicall to run one request per
        method. Done this way (rather than with a 'methods' argument)
        to preserve BC.
        """
        # First, build the query opts dict.
        if not opts:
            opts = dict()
        opts['decode'] = True
        opts['owner'] = 2745
        if isinstance(opts['method'], six.string_types):
            opts['method'] = (opts['method'],)
        if date:
            date = fedfind.helpers.date_check(date, fail_raise=True, out='obj')
            # We'll stretch the window by a day in either direction
            # just in case
            delta = datetime.timedelta(1)
            fromdate = date - delta
            todate = date + delta
            opts['createdAfter'] = fromdate.isoformat()
            opts['createdBefore'] = todate.isoformat()

        # Get the results. We use a multicall to run queries for all
        # requested methods with a single request.
        logger.debug("find_nightly_tasks: opts are %s", opts)
        multicall = xmlrpc_client.MultiCall(self)
        for method in opts['method']:
            methopts = opts.copy()
            methopts['method'] = method
            multicall.listTasks(methopts)
        tasks = list(itertools.chain.from_iterable(multicall()))

        # Filter the results. The request parameters - which we get as
        # a list under the key 'request' in the task dict - are not
        # *absolutely* consistent for the different methods, so we
        # have to make some assumptions. We assume that the datestamp
        # and the release are somewhere in the first four parameters.
        if release:
            tasks = [t for t in tasks
                     if any(str(p) == str(release).lower()
                            for p in t['request'][:3])]
        if date:
            # Filter down to ones for the specific date
            return [t for t in tasks
                    if any(p == date.strftime('%Y%m%d')
                           for p in t['request'][:4])]
        else:
            # Just return any with a version/release that looks like a
            # date (to help filter out any non-nightlies)
            return [t for t in tasks
                    if any(fedfind.helpers.date_check(p, fail_raise=False)
                           for p in t['request'][:4])]

    def find_task_images(self, task):
        """This finds the URLs for images produced by one or more Koji
        tasks, if it produced any. If it didn't, it raises an error.
        Returns a list of lists of URL strings. For BC, handles 'task'
        being a single task or an iterable of tasks.
        """
        if isinstance(task, dict):
            tasks = (task,)
        else:
            tasks = task
        logger.debug("Finding images for %s",
                     ' '.join(str(task['id']) for task in tasks))
        urls = self.find_task_urls(tasks, fedfind.const.IMAGE_EXTS)
        if not urls:
            # We have some files, but nothing that looks like an
            # image.
            raise fedfind.exceptions.NoImageError
        return urls

    def find_task_urls(self, task, exts):
        """This find files produced by the Koji task(s) 'task' whose
        names end with any of the extensions in the iterable 'exts'
        and returns their URLs. If no task has any files it will
        raise a NoFilesError exception; if no files with the specified
        extensions were found it will return an empty list. For BC,
        handles 'task' being a single task or an iterable of tasks.
        """
        if isinstance(task, dict):
            tasks = (task,)
        else:
            tasks = task
        # We can't use the file list from task['result'] because it
        # isn't updated when a task's files are aged out, so we can't
        # catch old composes where the files have now been deleted
        # that way.
        multicall = xmlrpc_client.MultiCall(self)
        for task in tasks:
            multicall.listTaskOutput(task['id'])
        results = zip(tasks, multicall())
        gotfiles = False
        urls = list()
        for (task, files) in results:
            if files:
                gotfiles = True
                matfiles = list()
                for fname in files:
                    if any(fname.endswith(ext) for ext in exts):
                        matfiles.append(fname)
                for matfile in matfiles:
                    url = "{0}/{1}/{2}".format(
                        fedfind.const.KOJI_BASE, taskrelpath(task['id']),
                        matfile)
                    urls.append(url)

        if not gotfiles:
            # No files - likely all failed or aged-out tasks.
            raise fedfind.exceptions.NoFilesError
        else:
            return urls
