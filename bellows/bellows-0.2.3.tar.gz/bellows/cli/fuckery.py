import asyncio
import datetime
import functools
import logging

import click

import bellows.ezsp
import bellows.types as t
import bellows.zigbee.application
import bellows.zigbee.zcl.foundation


LOGGER = logging.getLogger(__name__)


EZSP = None
APP = None

from . import util
from .main import main

@main.command()
@click.pass_context
def run(ctx):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_run(ctx))
    except KeyboardInterrupt:
        APP._ezsp.close()
        APP.save('zigbee.db')
    except:
        APP._ezsp.close()
        raise

@asyncio.coroutine
def _run(ctx):
    try:
        yield from __run(ctx)
    except:
        yield from asyncio.sleep(1)
        raise

@asyncio.coroutine
def __run(ctx):
    global APP, EZSP
    EZSP = bellows.ezsp.EZSP()
    # EZSP.add_callback(util.print_cb)
    yield from EZSP.connect(ctx.obj['device'])
    APP = bellows.zigbee.application.ControllerApplication(EZSP)
    yield from APP.startup()
    v = yield from EZSP.getNodeId()
    print("getNodeId = %s" % (v, ))

    EZSP.leaveNetwork()

    APP.load("zigbee.db")

    #click.echo("Permitting for 30s")
    #APP.permit(30)
    #click.echo("sleep(30)")
    #yield from asyncio.sleep(30)

    ieee = "00:0d:6f:00:05:7d:2d:34"
    ieee = t.EmberEUI64([t.uint8_t(p, base=16) for p in ieee.split(":")])
    dev = APP.devices[ieee]

    ieee = "00:0d:6f:00:05:97:9b:ec"
    ieee = t.EmberEUI64([t.uint8_t(p, base=16) for p in ieee.split(":")])
    switch = APP.devices[ieee]

    ieee = "00:0d:6f:00:0b:bc:8e:b6"
    ieee = t.EmberEUI64([t.uint8_t(p, base=16) for p in ieee.split(":")])
    door = APP.devices[ieee]

    #ieee = "d0:52:a8:00:e0:be:00:05"
    #ieee = t.EmberEUI64([t.uint8_t(p, base=16) for p in ieee.split(":")])
    #arrival_dev = APP.devices[ieee]

    zdo_reqs = [
        #(0x0000, dev._ieee, 0, 0),
        #(0x0001, dev._nwk, 0, 0),
        #(0x0005, dev._nwk),
        #(0x0004, dev._nwk, 1),
        #(0x0004, dev._nwk, 2),
    ]

    """
    print("Broadcast NWK address request for motion's IEEE")
    aps, data = dev.zdo._serialize(0, dev._ieee)
    v = yield from EZSP.sendBroadcast(0xfffe, aps, 0, aps.sequence, data)
    print(v)

    print("Broadcast NWK address request for switch's IEEE")
    aps, data = dev.zdo._serialize(0, switch._ieee)
    v = yield from EZSP.sendBroadcast(0xfffe, aps, 0, aps.sequence, data)
    print(v)

    print("ZDO requests to motion")
    for req in zdo_reqs:
        try:
            v = yield from dev.zdo.request(*req)
            print("ZDO response: %s" % (v, ))
        except Exception as e:
            print("ZDO failure: %s" % (e, ))
    """

    #reporting_config = bellows.zigbee.zcl.foundation.AttributeReportingConfig()
    #reporting_config.direction = 0
    #reporting_config.attrid = 0
    #reporting_config.datatype = 0x29
    #reporting_config.min_interval = 60
    #reporting_config.max_interval = 120
    #reporting_config.reportable_change = 100

    #print("ZCL configure reporting")
    #print(t.serialize([[reporting_config]], bellows.zigbee.zcl.foundation.COMMANDS[0x06][1]))
    #v = yield from dev.endpoints[1].clusters[0x0402].request(True, 0x06, bellows.zigbee.zcl.foundation.COMMANDS[0x06][1], [reporting_config])
    #print(v)

    bind_clusters = [
        #1,
        #0x0020,
        #0x0402,
        #0x0500,
        # 0xFC02,
    ]

    print("ZDO bind")
    for cluster in bind_clusters:
        v = yield from door.endpoints[1].clusters[cluster].bind()
        print("Cluster %s: %s" % (cluster, v))

    """
    print("Configure reporting")
    v = yield from dev.endpoints[1].clusters[0x0001].configure_reporting(0x20, 10800, 21600, 100)
    print(v)
    v = yield from dev.endpoints[1].clusters[0x0402].configure_reporting(0, 60, 120, 100)
    print(v)
    v = yield from dev.endpoints[1].clusters[0x0500].configure_reporting(0x0002, 0, 3600, 1)
    print(v)
    # v = yield from dev.endpoints[1].clusters[0xFC02].configure_reporting(0, 300, 900, 100)
    print("Writing alarm config")
    v = yield from dev.endpoints[1].clusters[0x0500].write_attributes({0x10: APP._ieee})
    print(v)
    #print("Setting checkin interval to 30 minutes")
    #v = yield from dev.endpoints[1].clusters[0x0020].write_attributes({0: 7200})
    #print(v)
    print("Alarm enroll response")
    v = yield from dev.endpoints[1].clusters[0x0500].command(0, 0, 0)
    """

    zcl_reqs = [
        # (0x0000, [0, 1, 2, 3, 4, 5, 6, 7, 8]),
        #(0x0001, [0x0030, 0x0033]),
        #(0x0020, [0, 1, 2, 3, 4, 5, 6]),
        #(0x0402, [0]),
        #(0x0500, [0, 1, 2, 0x0011, 0x0012, 0x0013]),
        #(0x0b05, [0, 0x011c, 0x011d]),
    ]

    print("ZCL attributes")
    for cluster_id, attrs in zcl_reqs:
        c = door.endpoints[1].clusters[cluster_id]
        print("Cluster %s (%s)" % (cluster_id, c.name))
        try:
            v = yield from c.read_attributes(attrs)
            for record in v[0]:
                if record.status != 0:
                    continue
                attr_name = c.attributes[record.attrid][0]
                print("  %s = %s" % (attr_name, record.value.value))
        except Exception as e:
            print("ZCL failure: %s" % (e, ))

    #print("ZCL command")
    #try:
    #    v = yield from dev.endpoints[1].clusters[0x0000].command(0)
    #    print(v)
    #except:
    #    print("ZCL command failure")

    #print("Permitting joins for 120s...")
    #yield from APP.permit(120)
    #print("Ready")
    #yield from asyncio.sleep(65)
    #print("Permit done")


    print("Switch commands!")
    v = yield from switch.endpoints[1].clusters[6].command(0)
    yield from asyncio.sleep(7)
    for i in range(5):
        v = yield from switch.endpoints[1].clusters[6].command(1)
        yield from asyncio.sleep(5)
        v = yield from switch.endpoints[1].clusters[6].command(0)
        yield from asyncio.sleep(5)


    print("Permitting for 30s")
    yield from APP.permit(30)
    yield from switch.endpoints[1].clusters[6].command(1)
    yield from asyncio.sleep(31)

    #print("Running.")
    #while True:
    #    yield from asyncio.sleep(60)
    #    print(datetime.datetime.now())

    # APP.save('zigbee.db')

