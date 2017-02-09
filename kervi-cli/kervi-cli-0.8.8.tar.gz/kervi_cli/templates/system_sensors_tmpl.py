# Copyright (c) 2016, Tim Wentzlau
# Licensed under MIT

""" Module that defines core cpu sensors """

from kervi.sensor import Sensor, SensorThread
import psutil

class CPULoadSensor(Sensor):
    """ Sensor that mesures cpu load on host """
    def __init__(self):
        Sensor.__init__(self, "CPULoadSensor", "CPU")
        self.max = 100
        self.min = 0
        self.unit = "%"
        self.store_to_db = False
        self.link_to_dashboard("*", "sys-header")
        self.link_to_dashboard("system", "cpu", type="value", size=2, link_to_header=True)
        self.link_to_dashboard("system", "cpu", type="chart", size=2)

        psutil.cpu_percent()
    def read_sensor(self):
        self.new_sensor_reading(psutil.cpu_percent())

class MemUseSensor(Sensor):
    """ Sensor that mesures memory use """
    def __init__(self):
        Sensor.__init__(self, "MemUse", "Memory")
        self.max = 100
        self.min = 0
        self.unit = "%"
        self.store_to_db = False
        self.store_delta = 0.01
        self.link_to_dashboard("*", "sys-header")
        self.link_to_dashboard("system", "memory", type="value", size=2, link_to_header=True)
        self.link_to_dashboard("system", "memory", type="chart", size=2)

        try:
            percent = psutil.virtual_memory().percent
        except:
            percent = psutil.phymem_usage().percent
        self.value = percent

    def read_sensor(self):
        try:
            percent = psutil.virtual_memory().percent
        except:
            percent = psutil.phymem_usage().percent
        self.new_sensor_reading(percent)

class DiskUseSensor(Sensor):
    """ Sensor that mesures disk use """
    def __init__(self):
        Sensor.__init__(self, "DiskUse", "Disk usage")
        self.reading_interval = 1
        self.max = 100
        self.min = 0
        self.unit = "%"
        self.store_to_db = False
        self.store_delta = 0.01
        self.link_to_dashboard("system", "disk", type="radial_gauge", size=1)

        percent = psutil.disk_usage('/').percent
        self.value = percent

    def read_sensor(self):
        percent = psutil.disk_usage('/').percent
        self.new_sensor_reading(percent)

SensorThread([CPULoadSensor(), MemUseSensor(), DiskUseSensor()])
