#!/usr/bin/env python

#
# Project:  juju-vnfm
# file:     asyncio_test
# created:  17/02/2017 
#

"""
description goes here
"""
import asyncio
import time

__author__ = "lto"
__maintainer__ = "lto"


async def run():
    time.sleep(2)
    print('https://docs.python.org/3/library/asyncio.html')
    time.sleep(2)
    asyncio.get_event_loop().stop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(run())
    loop.run_forever()