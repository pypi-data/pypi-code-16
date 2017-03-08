# !/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import time
import urllib
from threading import Thread

local_proxies = {'http': 'http://131.139.58.200:8080'}


class Download(Thread, urllib.FancyURLopener):
    def __init__(self, thread_name, url, filename, ranges=0, proxies={}):
        Thread.__init__(self, name=thread_name)
        urllib.FancyURLopener.__init__(self, proxies)
        self.name = thread_name
        self.url = url
        self.filename = filename
        self.ranges = ranges
        self.downloaded = 0

    def run(self):
        try:
            self.downloaded = os.path.getsize(self.filename)
        except OSError:
            self.downloaded = 0
        self.start_point = self.ranges[0] + self.downloaded
        if self.start_point >= self.ranges[1]:
            print 'Part %s has been downloaded over.' % self.filename
            return
        self.oneTimeSize = 16384  # 16kByte/time
        print 'task %s will download from %d to %d' % (self.name, self.start_point, self.ranges[1])
        self.addheader("Range", "bytes=%d-%d" %
                       (self.start_point, self.ranges[1]))
        self.url_handler = self.open(self.url)
        data = self.url_handler.read(self.oneTimeSize)

        while data:
            file_handler = open(self.filename, 'ab+')
            file_handler.write(data)
            file_handler.close()
            self.downloaded += len(data)
            data = self.url_handler.read(self.oneTimeSize)


def get_url_file_size(url, proxies={}):
    url_handler = urllib.urlopen(url, proxies=proxies)
    headers = url_handler.info().headers
    length = 0
    for header in headers:
        if header.find('Length') != -1:
            length = header.split(':')[-1].strip()
            length = int(length)
    return length


def split_block(totalsize, blocknumber):
    blocksize = totalsize / blocknumber
    ranges = []
    for i in range(0, blocknumber - 1):
        ranges.append((i * blocksize, i * blocksize + blocksize - 1))
    ranges.append((blocksize * (blocknumber - 1), totalsize - 1))
    return ranges


def islive(tasks):
    for task in tasks:
        if task.isAlive():
            return True
    return False


def mdx(url, output, blocks=6, proxies=local_proxies):
    size = get_url_file_size(url, proxies)
    ranges = split_block(size, blocks)

    name = os.path.basename(output)
    thread_name = [name + "_thread_%d" % i for i in range(0, blocks)]
    filename = [name + "_tmpfile_%d" % i for i in range(0, blocks)]

    tasks = []
    for i in range(0, blocks):
        task = Download(thread_name[i], url, filename[i], ranges[i])
        task.setDaemon(True)
        task.start()
        tasks.append(task)

    time.sleep(2)
    while islive(tasks):
        downloaded = sum([task.downloaded for task in tasks])
        process = downloaded / float(size) * 100
        show = u'\rFilesize:%d Downloaded:%d Completed:%.2f%%' % (
            size, downloaded, process)
        sys.stdout.write(show)
        sys.stdout.flush()
        time.sleep(0.5)

    file_handler = open(output, 'wb+')
    for i in filename:
        f = open(i, 'rb')
        file_handler.write(f.read())
        f.close()
        try:
            os.remove(i)
            pass
        except:
            pass

    file_handler.close()


def md(url, output):
    return mdx(url, output, blocks=6, proxies={})


if __name__ == '__main__':
    url = 'http://dldir1.qq.com/qqfile/QQforMac/QQ_V3.1.1.dmg'
    output = 'download.file'
    md(url, output)
