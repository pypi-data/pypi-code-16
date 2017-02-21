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
import logging
import time
import traceback

from juju.model import Model


async def deploy_local_charm(charm_dir_path, application_name, number_of_units, machine_number=None, model=None,
                             series='trusty'):
    model = Model()
    await model.connect_current()
    print("model: %s" % model)
    application = await model.deploy(charm_dir_path,
                                     application_name,
                                     num_units=number_of_units,
                                     series=series,
                                     to=[dict(scope='#', directive=str(machine_number))])
    print("application: %s" % application)
    model.loop.stop()


async def status():
    try:
        model = Model()
        await model.connect_current()

        print("model: %s" % model)

        print("applications %s" % model.applications)

        print(list(model.units.values())[0].data)

    except Exception as e:
        traceback.print_exc()
    finally:
        await model.disconnect()
        model.loop.stop()


loop = asyncio.get_event_loop()
loop.create_task(deploy_local_charm("/opt/openbaton/juju-charm", "juju-charm-test", 1, 121))
loop.run_forever()
