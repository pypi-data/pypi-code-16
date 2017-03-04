# Copyright (c) 2016, Tim Wentzlau
# Licensed under MIT

""" Module that defines core cpu sensors """

from kervi.sensor import Sensor, SensorThread
from kervi_devices.platforms.common.sensors.cpu_use import CPULoadSensorDeviceDriver
from kervi_devices.platforms.common.sensors.memory_use import MemUseSensorDeviceDriver
from kervi_devices.platforms.common.sensors.disk_use import DiskUseSensorDeviceDriver


cpu_sensor = Sensor("CPULoadSensor","CPU", CPULoadSensorDeviceDriver())
cpu_sensor.store_to_db = False
cpu_sensor.link_to_dashboard("*", "sys-header")
cpu_sensor.link_to_dashboard("system", "cpu", type="value", size=2, link_to_header=True)
cpu_sensor.link_to_dashboard("system", "cpu", type="chart", size=2)

mem_sensor = Sensor("MemLoadSensor", "Memory", MemUseSensorDeviceDriver())
mem_sensor.store_to_db = False
mem_sensor.link_to_dashboard("*", "sys-header")
mem_sensor.link_to_dashboard("system", "memory", type="value", size=2, link_to_header=True)
mem_sensor.link_to_dashboard("system", "memory", type="chart", size=2)

disk_sensor = Sensor("DiskUseSensor", "Disk", DiskUseSensorDeviceDriver())
disk_sensor.store_to_db = False
disk_sensor.link_to_dashboard("*", "sys-header")
disk_sensor.link_to_dashboard("system", "disk", type="vertical_linear_gauge", size=2)
