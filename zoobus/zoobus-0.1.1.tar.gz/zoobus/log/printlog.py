#coding=utf8

import os
import sys
import logging
import logging.handlers
import datetime


def logprint(logname, path, level=logging.DEBUG, max_bytes=1024*1024*20,
             backup_count=0, to_stdout=True):
    """
    :param logname:  logger name
    :param path:  log path
    """
    logger = logging.getLogger(logname)
    frt = logging.Formatter('%(message)s')
    hdr = None
    if path:
        hdr = logging.handlers.RotatingFileHandler(path, 'a', max_bytes, backup_count, 'utf-8')
        hdr.setFormatter(frt)
        hdr._name = logname + '_p'
        already_in = False
        for _hdr in logger.handlers:
            if _hdr._name == logname + '_p':
                already_in = True
                break
        if not already_in:
            logger.addHandler(hdr)
    if to_stdout:
        hdr = logging.StreamHandler(sys.stdout)
        hdr.setFormatter(frt)
        hdr._name = logname + '_s'
        already_in = False
        for _hdr in logger.handlers:
            if _hdr._name == logname + '_s':
                already_in = True
                break
        if not already_in:
            logger.addHandler(hdr)
    logger.setLevel(level)

    def _wraper(*args):
        if not args:
            return
        encoding = 'utf8' if os.name == 'posix' else 'gb18030'
        args = [_cu(a, encoding) for a in args]
        f_back = None
        try:
            raise Exception
        except:
            f_back = sys.exc_traceback.tb_frame.f_back
        f_name = f_back.f_code.co_name
        filename = os.path.basename(f_back.f_code.co_filename)
        m_name = os.path.splitext(filename)[0]
        logger.info(u' '.join([u'[%s]'%unicode(datetime.datetime.now()), 
                     ' '.join(args)]))
    return _wraper, logger


def _cu(string, encoding):
    if isinstance(string, unicode):
        return string
    elif isinstance(string, str):
        return string.decode(encoding)
    else:
        return str(string)
