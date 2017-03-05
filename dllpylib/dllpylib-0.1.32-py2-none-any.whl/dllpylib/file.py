# -*- coding: utf-8 -*-
""" Python Library by DLL (and for DLL) """

import os
from datetime import datetime


def recent_files(count, fname_list, quiet=False, delete=False):
    """ Among file names given in 'filename_list' (conditionaly)
        retain only 'count' most 'fresh' ones and delete others.
        If:
            quiet is True then no message will be displayed.
            delete is True then unneeded files will be actually deleted.
    """
    ctimes = sorted([(datetime.fromtimestamp(os.stat(fname).st_mtime), fname) for fname in fname_list],
                    key=lambda x: x[0],
                    reverse=True)
    to_retain = ctimes[:count]
    to_delete = ctimes[count:]
    if not quiet:
        print(("\n".join(["+%s %s " % item for item in to_retain])))
        print(("\n".join(["-%s %s " % item for item in to_delete])))
    if delete:
        for pair in to_delete:
            os.unlink(pair[1])
