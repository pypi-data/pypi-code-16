#!/usr/bin/env python
import time
from sys import exit

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from prometheus_client.core import CounterMetricFamily

from smeterd import __default_serial__
from smeterd.meter import SmartMeter


__version__ = '0.9.2'


class SmeterdCollector(object):
    def collect(self):
        with SmartMeter(__default_serial__) as meter:
            p = meter.read_one_packet()

        yield CounterMetricFamily('smart_meter_gas_total', 'The total gas consumed', value=int(p['gas']['total']*1000))

        kwh = CounterMetricFamily('smart_meter_kwh_total', 'The total kwh consumed', labels=["tariff"])
        kwh.add_metric(['low'], int(p['kwh']['low']['consumed']*1000))
        kwh.add_metric(['high'], int(p['kwh']['high']['consumed']*1000))

        yield kwh


def main():
    port = 8090
    try:
        REGISTRY.register(SmeterdCollector())
        start_http_server(port)
        print("Serving at port: {}".format(port))
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted")
        exit(0)


if __name__ == '__main__':
    main()
