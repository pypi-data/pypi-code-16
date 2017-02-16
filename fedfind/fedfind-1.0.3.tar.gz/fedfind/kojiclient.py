#!/usr/bin/python2

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

"""A subclass of koji.ClientSession to handle Koji interaction with a
couple of custom methods.
"""

import datetime
import koji

import fedfind.const
import fedfind.exceptions
import fedfind.helpers

class ClientSession(koji.ClientSession):
    """Add a couple of methods to find nightly image files."""
    def __init__(self, *args, **kwargs):
        super(ClientSession, self).__init__(*args, **kwargs)

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
        """
        # First, build the query opts dict.
        if not opts:
            opts = dict()
        opts['decode'] = True
        opts['owner'] = 2745
        if date:
            # We'll stretch the window by a day in either direction
            # just in case
            delta = datetime.timedelta(1)
            fromdate = date - delta
            todate = date + delta
            opts['createdAfter'] = fromdate.isoformat()
            opts['createdBefore'] = todate.isoformat()

        # Now find and filter the results. The request parameters -
        # which we get as a list under the key 'request' in the task
        # dict - are not *absolutely* consistent for the different
        # methods, so we have to make some assumptions. We assume that
        # the datestamp and the release are somewhere in the first
        # four parameters.
        tasks = self.listTasks(opts)
        if release:
            tasks = [t for t in tasks
                     if any(str(p) == str(release) for p in t['request'][:3])]
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

    def find_task_url(self, task):
        """This finds the URL for the image produced by a Koji task,
        if it produced any. If it didn't, it raises an error. It
        assumes a task will only ever produce *one* image; if it
        produces more than one, you'll get the last one Koji gives us.
        """
        # We can't use the file list from task['result'] because it
        # isn't updated when a task's files are aged out, so we can't
        # catch old composes where the files have now been deleted
        # that way.
        files = self.listTaskOutput(task['id'])
        if files:
            imgfile = None
            for fname in files:
                for ext in fedfind.const.IMAGE_EXTS:
                    if fname.endswith(ext):
                        imgfile = fname
            if imgfile:
                url = "{0}/{1}/{2}".format(
                    fedfind.const.KOJI_BASE,
                    koji.pathinfo.taskrelpath(task['id']), imgfile)
                return url
            else:
                # We have some files, but nothing that looks like an
                # image.
                raise fedfind.exceptions.NoImageError
        else:
            # No files - likely a failed or aged-out task.
            raise fedfind.exceptions.NoFilesError
