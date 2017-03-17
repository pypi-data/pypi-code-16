# -*- coding: utf-8 -*-

import time


def ms_now():
    """Get current timestamp in milliseconds
    """
    return int(time.time() * 1000)
