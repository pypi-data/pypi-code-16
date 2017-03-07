#!/usr/bin/env python
# -*- coding: utf-8 -*-

def _log_fail(log, e):
    if log is None:
        traceback.print_exc()
    else:
        log.LevPrint("ERROR", "connect logserver fail %s" % str(e), True)
