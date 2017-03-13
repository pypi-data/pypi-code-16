# The MIT License (MIT)
#
# Copyright (c) 2015 - 2017 imm studios, z.s.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import tempfile
import stat
import uuid
import time

from .logging import *
from .common import PYTHON_VERSION, get_guid

__all__ = ["get_files", "get_temp", "get_base_name", "file_to_title", "get_file_siblings", "WatchFolder"]


def get_files(base_path, **kwargs):
    #TODO: Use os.scandir if python version >= 3.5
    recursive = kwargs.get("recursive", False)
    hidden = kwargs.get("hidden", False)
    relative_path = kwargs.get("relative_path", False)
    case_sensitive_exts = kwargs.get("case_sensitive_exts", False)
    if case_sensitive_exts:
        exts = kwargs.get("exts", [])
    else:
        exts = [ext.lower() for ext in kwargs.get("exts", [])]
    strip_path = kwargs.get("strip_path", base_path)
    if os.path.exists(base_path):
        for file_name in os.listdir(base_path):
            if not hidden and file_name.startswith("."):
                continue
            file_path = os.path.join(base_path, file_name)
            try:
                is_reg = stat.S_ISREG(os.stat(file_path)[stat.ST_MODE])
                is_dir = stat.S_ISDIR(os.stat(file_path)[stat.ST_MODE])
            except Exception:
                continue
            if is_reg:
                ext = os.path.splitext(file_name)[1].lstrip(".")
                if not case_sensitive_exts:
                    ext = ext.lower()
                if exts and ext not in exts:
                    continue
                if relative_path:
                    yield file_path.replace(strip_path, "", 1).lstrip(os.path.sep)
                else:
                    yield file_path
            elif is_dir and recursive:
                for file_path in get_files(
                            file_path,
                            recursive=recursive,
                            hidden=hidden,
                            case_sensitive_exts=case_sensitive_exts,
                            exts=exts,
                            relative_path=relative_path,
                            strip_path=strip_path
                        ):
                    yield file_path


def get_temp(extension=False, root=False):
    if not root:
        root = tempfile.gettempdir()
    filename = os.path.join(root, get_guid())
    if extension:
        filename = filename + "." + extension
    return filename


def get_base_name(fname):
    return os.path.splitext(os.path.basename(fname))[0]


def file_to_title(fname):
    base = get_base_name(fname)
    base = base.replace("_"," ").replace("-"," - ").strip()
    elms = []
    capd = False
    for i, elm in enumerate(base.split(" ")):
        if not elm: continue
        if not capd and not (elm.isdigit() or elm.upper()==elm):
            elm = elm.capitalize()
            capd = True
        elms.append(elm)
    return " ".join(elms)


def get_file_siblings(path, exts=[]):
    #TODO: Rewrite this
    root = os.path.splitext(path)[0]
    for f in exts:
        tstf = root + "." + f
        if os.path.exists(tstf):
            yield tstf


def get_file_size(path):
    try:
        f = open(path, "rb")
    except Exception:
        log_traceback("Exception! File {} is not accessible".format(path))
        return 0
    f.seek(0, 2)
    return f.tell()


class WatchFolder():
    def __init__(self, input_dir, **kwargs):
        self.input_dir = input_dir
        self.settings = self.defaults
        self.settings.update(**kwargs)
        self.file_sizes = {}
        if "valid_exts" in kwargs:
            logging.warning("Watchfolder: valid_exts is deprecated. Use exts instead")
            self.settings["exts"] = kwargs["valid_exts"]
        self.ignore_files = set()

    def __getitem__(self, key):
        return self.settings[key]

    @property
    def defaults(self):
        settings = {
            "iter_delay" : 5,
            "hidden" : False,
            "relative_path" : False,
            "case_sensitive_exts" : False,
            "recursive" : True,
            "exts" : []
            }
        return settings

    def start(self):
        while True:
            try:
                self.watch()
                self.clean_up()
                time.sleep(self.settings["iter_delay"])
            except KeyboardInterrupt:
                print ()
                logging.warning("User interrupt")
                break

    def clean_up(self):
        keys = [key for key in self.file_sizes.keys()]
        for file_path in keys:
            if not os.path.exists(file_path):
                del(self.file_sizes[file_path])

    def watch(self):
        for input_path in get_files(
                    self.input_dir,
                    recursive=self.settings["recursive"],
                    hidden=self.settings["hidden"],
                    exts=self.settings["exts"],
                    relative_path=self.settings["relative_path"],
                    case_sensitive_exts=self.settings["case_sensitive_exts"]
                ):

            if self["relative_path"]:
                full_path = os.path.join(self.input_dir, input_path)
            else:
                full_path = input_path

            if full_path in self.ignore_files:
                continue

            self.process_file_size = get_file_size(full_path)
            if self.process_file_size == 0:
                continue

            if not (full_path in self.file_sizes.keys() and self.file_sizes[full_path] == self.process_file_size):
                self.file_sizes[full_path] = self.process_file_size
                logging.debug("Watching file {}".format(input_path))
                continue
            self.process(input_path)

    def process(self, input_path):
        pass

