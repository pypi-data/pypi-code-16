# The MIT License (MIT)
#
# Copyright (c) 2017 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import time
from threading import Thread
from os import stat, unlink, listdir, rmdir
from os.path import join, basename, dirname, isdir, isfile, exists
from io import BytesIO
import xml.etree.ElementTree as ET
import hcpsdk

import hcpup


class Uploader(Thread):
    """
    File uploading thread.
    """
    def __init__(self, conf, target, queues, *args, **kwargs):
        """
        :param conf:        the config object
        :param target:      the hcpsdk.Target object to use to talk to HCP
        :param queues:      the queues object (queues.queue hold the files to
                            upload)
        """
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__+'.Uploader')
        self.conf = conf
        self.target = target
        self.queues = queues

    def run(self):
        """
        Run the uploader thread.
        """
        self.logger.debug('{} started'.format(self.name))

        try:
            if self.conf['obfuscate']:
                pb = hcpsdk.pathbuilder.PathBuilder(
                    initialpath=join('/rest', self.conf['path']), annotation=True)

            con = hcpsdk.Connection(self.target, retries=3)

            while True:
                prio, item = self.queues.queue.get()
                self.logger.debug('{} got "{}" from queue'.format(self.name, item))
                self.queues.queue.task_done()

                if item == '!**exit**!':
                    self.logger.debug('{} exiting'.format(self.name))
                    break

                # skip directories
                if isdir(item):
                    self.logger.debug('{} is a directory - skipping'
                                      .format(item))
                    continue

                try:
                    with open(item, 'rb') as itemhdl:
                        if self.conf['obfuscate']:
                            px = pb.getunique(item)
                            url = join(px[0], px[1])
                            annotation = self.fixannotation(item, px[2])
                        else:
                            url = join('/rest', self.conf['path'],
                                       item[len(self.conf['watchdir']) + 1:])

                        try:
                            con.PUT(url, body=itemhdl)
                        except Exception as e:
                            self.logger.exception('PUT {} ({}) failed'.format(url,
                                                                              item))
                        else:
                            if con.response_status != 201:
                                self.logger.warning('PUT {} ({}) failed - {}-{}'
                                                    .format(url, item,
                                                            con.response_status,
                                                            con.response_reason))
                            else:
                                self.logger.debug('PUT {} ({}) succeeded'.format(url,
                                                                                 item))

                                if not self.conf['obfuscate']:
                                    if self.conf['delete after upload']:
                                        try:
                                            unlink(item)
                                        except Exception as e:
                                            self.logger.warning(
                                                'failed to unlink {}'.format(item))
                                        else:
                                            self.logger.debug(
                                                'successfully unlinked {}'.format(
                                                    item))
                                    continue

                                try:
                                    con.PUT(url, body=annotation,
                                            params={'type': 'custom-metadata',
                                                    'annotation': self.conf[
                                                        'annotation']})
                                except Exception as e:
                                    self.logger.exception(
                                        'PUT annotation for {} ({}) failed'
                                            .format(url, item))
                                else:
                                    if con.response_status != 201:
                                        self.logger.warning(
                                            'PUT annotation for{} ({}) failed - {}-{}'
                                            .format(url, item,
                                                    con.response_status,
                                                    con.response_reason))
                                    else:
                                        self.logger.debug(
                                            'PUT annotation for {} ({}) succeeded'
                                                .format(url, item))

                                        if self.conf['delete after upload']:
                                            try:
                                                unlink(item)
                                            except Exception as e:
                                                self.logger.warning(
                                                    'failed to unlink {}'.format(item))
                                            else:
                                                self.logger.debug(
                                                    'successfully unlinked {}'.format(
                                                        item))

                                                # try to delete the folder as well...
                                                if self.conf['remove empty folders after upload']:
                                                    self.rmfolder(item)


                except Exception as f:
                    self.logger.debug('upload of {} failed...\n\thint: {}'
                                      .format(item, f))

        except Exception as e:
            self.logger.exception(
                'Uploader failed!!!')

    def fixannotation(self, item, annotation):
        """
        Fix the annotation by adding additional attributes.

        :param item:        the file picked from the queue
        :param annotation:  the annotation from hcpsdk.pathbuilder
        :return:            the new annotation
        """
        root = ET.fromstring(annotation)
        if self.conf['tag_timestamp']:
            root.set('timestamp', str(int(stat(item).st_ctime)))
        root.set('note', self.conf['tag_note'])

        et = ET.ElementTree(element=root)
        with BytesIO() as xmlstring:
            et.write(xmlstring, encoding="utf-8", method="xml",
                     xml_declaration=True)
            annotation = xmlstring.getvalue().decode()
            self.logger.debug(hcpup.log.dpprint('annotation:', annotation))

        return annotation

    def rmfolder(self, item):
        """
        Try to remove a path up to watchdir.

        :param item: the path/filename to which the path shall be removed
        """
        while True:
            item = dirname(item)
            if item == self.conf['watchdir']:
                break

            try:
                rmdir(item)
            except OSError:
                pass
            else:
                wd = self.queues.watchmgr.get_wd(item)
                self.logger.debug('watchmgr.get_wd({}) = {}'.format(item, wd))
                self.queues.watchmgr.del_watch(wd)
                if item in self.queues.ddict.keys():
                    del self.queues.ddict[item]
                self.logger.debug('successfully removed dir {} {}'
                                  .format(item,
                                          '(and its inotify watch)' if wd else ''))


class DirCrawler(Thread):
    """
    Directory Crawler - used to find files in dirs not processed by inotify.
    """
    def __init__(self, queues, *args, **kwargs):
        """
        :param queues:      the queues object (queues.queue hold the files to
                            upload)
        """
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__+'.DirCrawler')
        self.queues = queues

    def run(self):
        """
        Run the uploader thread.
        """
        self.logger.debug('{} started'.format(self.name))

        try:
            while True:
                prio, dir = self.queues.rvqueue.get()
                self.logger.debug('{} got "{}" from rvqueue'.format(self.name, dir))
                self.queues.rvqueue.task_done()

                if dir == '!**exit**!':
                    self.logger.debug('{} exiting'.format(self.name))
                    break

                # get a list of all entries in dir
                try:
                    files = listdir(dir)
                except Exception as e:
                    self.logger.warning('unable to list folder {}'.format(dir))
                    continue

                # find the files in dir that haven't been tracked by inotify
                if files:
                    with self.queues.rvlock:
                        self.logger.debug('*** lock set ({}) ***'.format(self.name))
                        self.logger.debug(hcpup.log.dpprint(
                            'files in {} already noticed by inotify:\n\t'
                                .format(dir),
                            self.queues.rvdict[
                                dir] if dir in self.queues.rvdict.keys() else []))
                        if dir in self.queues.rvdict.keys():
                            leftfiles = [join(dir,x) for x in files if join(dir,x) not in self.queues.rvdict[dir]]
                            del self.queues.rvdict[dir]
                        else:
                            leftfiles = [join(dir,x) for x in files]

                        self.logger.debug(hcpup.log.dpprint(
                            'files in {} not noticed by inotify:'.format(dir), leftfiles))

                        for f in leftfiles:
                            self.logger.debug('putting into queue: {}'.format(f))
                            self.queues.queue.put((9, f))
                            self.queues.dcdict[f] = time.time()
                        self.logger.debug(
                            '*** lock released ({}) ***'.format(self.name))

        except Exception as e:
            self.logger.exception('DirCrawler failed!!!')


def startuploaders(conf, target):
    """
    Start the uploader threads.

    :param conf:    the config object
    :param target:  the hcpsdk.Target object to use to talk to HCP
    """
    logger = logging.getLogger(__name__+'.startuploaders')
    logger.debug('starting {} uploader thread(s)'
                 .format(conf['upload threads']))

    # queues (and cleanup thread)
    uwts = [hcpup.queue.Queues(name='queues')]

    # uploader threads
    uwts += [Uploader(conf, target, uwts[0], name='uploader-{:02d}'.format(i))
             for i in range(conf['upload threads'])]

    # dir crawler thread(s)
    uwts.append(DirCrawler(uwts[0], name='dircrawler'))

    for t in uwts:
        t.setDaemon(True)
        t.start()

    return uwts

def createtarget(conf):
    """
    Create a hcpsdk.Target object used by the uploader threads.

    :param conf:    the dict from the config file
    :return:        the hcpsdk.Target object
    """
    logger = logging.getLogger(__name__+'.createtarget')
    logger.debug('setting up hcpsdk.Target({}, auth, port={})'
                 .format(conf['namespace'], 443 if conf['ssl'] else 80))

    return hcpsdk.Target(conf['namespace'],
                         hcpsdk.NativeAuthorization(conf['user'],
                                                    conf['password']),
                         port=443 if conf['ssl'] else 80,
                         dnscache=conf['local DNS resolver'])
