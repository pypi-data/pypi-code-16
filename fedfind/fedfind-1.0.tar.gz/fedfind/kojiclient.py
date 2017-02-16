#!/bin/python2

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
#
# This file provides a subclass of koji.ClientSession to handle Koji
# interaction with a couple of custom methods, and a hacky function
# to make sure we only use one client session.

import datetime
import koji

import fedfind.const
import fedfind.exceptions
import fedfind.helpers

def get_client():
    """If anyone knows a less ugly way of doing this, please do
    enlighten me. Sometimes we can get away without a Koji client
    session at all, so we don't want to just create one globally
    unconditionally, but if we need one, we only ever need *one*,
    and we might need it from any old place."""
    global kojiclient
    try:
        return kojiclient
    except:
        kojiclient = ClientSession('http://koji.fedoraproject.org/kojihub', {})
        return kojiclient

class ClientSession(koji.ClientSession):
    def __init__(self, *args, **kwargs):
        super(ClientSession, self).__init__(*args, **kwargs)

    def find_nightly_tasks(self, date=None, release=None, opts=dict()):
        """This is basically a wrapper around koji's listTasks() which
        will only return tasks that look like nightly image builds. If
        you pass date (as a datetime.date instance) it will find only
        nightlies from that date, by searching a window padded one day
        in either direction and then filtering down by a task request
        parameter which specifies the date. If you pass release (as a
        string, a Fedora release number or 'rawhide') it will find only
        nightlies for that release, by checking another request parameter.
        You can pass opts as a dict of query options, as listTasks()
        expects, and they will be passed through, except for 'decode'
        (which we need to be True to do the filtering) and 'createdAfter'
        and 'createdBefore' if you pass date (so just do one or the other).
        """
        opts['decode'] = True
        # The 'request' will be a list of task request parameters:
        # [name, version, release, arch...]
        # Because God hates us, in cloud nightly builds, 'release' is the
        # Fedora release and 'version' is the nightly date, but for all
        # other nightlies (seemingly), 'version' is the Fedora release and
        # 'release' is the date. So, handle that.
        if opts['method'] == 'createImage':
            datefield = 1
            releasefield = 2
        else:
            datefield = 2
            releasefield = 1
        if date:
            # We'll stretch the window by a day in either direction just in case
            delta = datetime.timedelta(1)
            fromdate = date - delta
            todate = date + delta
            opts['createdAfter'] = fromdate.isoformat()
            opts['createdBefore'] = todate.isoformat()
        tasks = self.listTasks(opts)
        if release:
            tasks = [t for t in tasks if t['request'][releasefield] == release]
        if date:
            # Filter down to ones for the specific date
            return [t for t in tasks
                     if t['request'][datefield] == date.strftime('%Y%m%d')]
        else:
            # Just return any with a version/release that looks like a date (to
            # filter out non-nightlies)
            return [t for t in tasks if
                     fedfind.helpers.datecheck(t['request'][datefield])]

    def find_task_url(self, task):
        """This finds the URL for the image produced by a Koji task,
        if it produced any. If it didn't, it raises an error. It basically
        assumes a task will only ever produce *one* image; if it produces
        more than one, you'll get the last one Koji gives us.
        """
        # We can't use the file list from task['result'] because it isn't
        # updated when a task's files are aged out, so we can't catch old
        # composes where the files have now been deleted that way.
        files = self.listTaskOutput(task['id'])
        if files:
            for f in files:
                for ext in fedfind.const.IMAGE_EXTS:
                    if f.endswith(ext):
                        fname = f
            if fname:
                url = "{}/{}/{}".format(
                        fedfind.const.KOJI_BASE,
                        koji.pathinfo.taskrelpath(task['id']), fname)
                return url
            else:
                # We have some files, but nothing that looks like an image.
                raise fedfind.exceptions.NoImageError
        else:
            # No files - likely a failed or aged-out task.
            raise fedfind.exceptions.NoFilesError
