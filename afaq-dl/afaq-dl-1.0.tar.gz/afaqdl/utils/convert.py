# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:expandtab

# Copyright 2016 juxor <ju@riseup.net>

# This file is part of afaq-dl.
#
# afaq-dl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# afaq-dl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with afaq-dl.  If not, see <http://www.gnu.org/licenses/>.

""""""

import logging
import io
import subprocess
import html2text
from os import listdir, makedirs
from os.path import join, splitext, isdir
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


__all__ =  ['convert_dir', 'html2md', 'html2txt', 'html2txtbs', 'write_text']

def html2md(text):
    h = html2text.HTML2Text()
    if not isinstance(text, unicode):
        text = text.decode('utf-8', errors='ignore')
    md = h.handle(text)
    # fix links
    md = "\n".join([line.replace('.html', '.md') for line in
                    md.split('\n')
                    if line.find('http') <= -1])
#    # remove trailing whitespaces
#    md = "\n".join([line.replace(' \n', '\n') for line in
#                    md.split('\n')])
    return md


def html2txtbs(text):
    logger.info('Converting html to txt with BS.')
    soup = BeautifulSoup(text, "lxml")
    return soup.get_text()


def html2txt(command, html_path):
    logger.info('Converting html to txt using %s.', command)
    p = subprocess.call([command, 'build', html_path])
    return p


def write_text(path, filename, ext, text):
    filepath = join(path, filename + ext)
    logger.debug('Writing file %s', filepath)
    with io.open(filepath, 'w') as f:
            f.write(text)


def convert_dir(html_path, dst_path, convert_function, ext):
    if not isdir(dst_path):
        makedirs(dst_path)
    for html_file in listdir(html_path):
        filename, fileext = splitext(html_file)
        if fileext == '.html':
            html_file_path = join(html_path, html_file)
            logger.info('Converting html to markdown %s.',
                        html_file_path)
            logger.debug('Reading file %s', join(html_path, html_file))
            with io.open(html_file_path, 'r') as f:
                text = f.read()
            converted_text = convert_function(text)
            write_text(dst_path, filename, ext, converted_text)
