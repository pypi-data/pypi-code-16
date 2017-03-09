"""

Copyright (C) 2015-2016 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

originally added by Catherine Holloway
"""

# !/usr/bin/env python
from threading import Thread, enumerate
import sys
from time import time, sleep
from configparser import ConfigParser
from enum import Enum
import json
import logging
from os.path import join, dirname, abspath

# TODO: change instruments to a package to avoid this nonsense
#sys.path.append(join(dirname(abspath(__file__)), "device_drivers/can"))
from device_drivers.can.motor import Motor, get_hardware_info, PROPERTIES
from device_drivers.can.can_helpers import lookup_trace_variable_unit_name
from schema_forms.ADP05518 import TRACE_VARIABLES, FORM_DICT, SCHEMA_DICT
from device_drivers.can.CANcard import CanFrame

from gateway_helpers import get_logger
from coroutine_gateway import CoroutineGateway, url_go

cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']
CONFIG_URL = 'https://' + COMMON_SETTINGS['DOMAIN']
BREATH_TIME = 0.001


class MotorState(Enum):
    IDLE = 0
    HOMING = 1
    MOVING = 2



def test_api():
    mc = MotorCommunicator(CLIENT_SETTINGS['CANOPEN_ADDRESS'])
    _ = mc.get_health()
    mc.post_health()
    mc.post_config_form()
    mc.post_status(mc.card.status)
    mc.post_hardware_info()
    print("frames list: ", len(mc.card.frames_list))
    _point = {'measure_time': time() - mc.start_time}
    for parameter in ['actual_position', 'actual_velocity']:
        _point[parameter] = mc.card.property_getter(parameter)
    mc.test_run_id = 0
    mc.data_points.append(_point)
    mc.post_data()
    mc.get_data()
    mc.card.logs.append("hello world")
    mc.post_log(mc.card.logs[-1])
    mc.post_frame(mc.card.frames_list[-1])
    frames = mc.get_frame()
    print("got frame: ", frames)
    mc.update_frame({'frame_index': frames["frame_index"],
                     "explanation": "test explanation change",
                     "written": True})

logger = get_logger(log_filename=CLIENT_SETTINGS['DEFAULT_LOGFILE'])


def watcher():
    start_time = time()
    init_threads = enumerate()
    while True:
        sleep(BREATH_TIME)
        curr_threads = enumerate()
        if len(curr_threads) < len(init_threads):
            for _thread in init_threads:
                if _thread not in curr_threads:
                    elapsed = time()-start_time
                    logger.error(_thread.name+" failed after: "+str(elapsed))
                    eval("sudo service motor_gateway restart")
            init_threads = curr_threads



def run_gateway():
    mc = MotorCommunicator(CLIENT_SETTINGS['CANOPEN_ADDRESS'])
    sht = Thread(target=mc.health_thread, name="health")
    sst = Thread(target=mc.send_status, name="send_status")
    sdt = Thread(target=mc.sync_device, name="sync_device")
    rtt = Thread(target=mc.run_test, name="run_test")
    ltt = Thread(target=mc.log_threads, name="log_threads")
    cbt = Thread(target=mc.canbus_threads, name="canbus_threads")
    wt = Thread(target=watcher, name="watcher")
    sht.start()
    sst.start()
    sdt.start()
    rtt.start()
    ltt.start()
    cbt.start()
    wt.start()


class MotorCommunicator(CoroutineGateway):
    def __init__(self, motor):
        super(MotorCommunicator, self).__init__()
        self.status_url = url_go("/motor/status")
        self.data_url = url_go("/motor/data")
        self.test_info_url = url_go("/motor/test_information")
        self.hardware_info_url = url_go("/motor/hardware_information")
        self.canbus_url = url_go("/motor/canbus")
        self.start_time = time()
        self.end_time = None
        self.card = Motor(motor)
        self.card.open(baud=1000000)
        self.card.clear_pdos()
        self.angular_form = ANGULAR_FORM
        self.prev_status = []
        self.config_parts = ["motor_end_position", "properties",
                             "time_window", "trace"]
        self.hardware = get_hardware_info(self.card)
        self.instrument_name = "CopleyAccelNet:"+self.hardware['model_number']
        self.canbus_on = True
        # parameters are stored in json format, need to be converted to
        # capitalized spaces for motor controller
        self.data_points = []
        self.sync_on = False
        self.last_frame = -1

    def gen_data(self):
        return {"test_run_id": self.test_run_id}

    def convert_numpy_points(self):
        # removes numpy datatypes from data
        for i in range(len(self.data_points)):
            for key in self.data_points[i].keys():
                # purely for typing reduction
                dp = self.data_points[i][key]
                self.data_points[i][key] = dp if type(dp) == str or type(
                    dp) == bool else float(dp)

    def post_hardware_info(self):
        _data = {"gateway": COMMON_SETTINGS['HARDWARENAME']}
        _data.update(self.hardware)
        response = self.session.post(self.hardware_info_url,
                                     headers=self.headers,
                                     data=json.dumps(_data))
        assert response.status_code == 200

    def get_data(self):
        _data = self.gen_data()
        response = self.session.get(self.data_url, headers=self.headers,
                                    params=json.dumps(_data))
        assert response.status_code == 200

    def post_data(self):
        self.convert_numpy_points()
        _data = self.gen_data()
        _data["data"] = self.data_points
        _data["units"] = {}
        for key in self.data_points[0].keys():
            if key in PROPERTIES.keys():
                _data["units"][key] = PROPERTIES[key]["units"]
            elif key in TRACE_VARIABLES:
                _data["units"][key] = lookup_trace_variable_unit_name(key)
        print("sending ", len(self.data_points), "points, testid: ", self.test_run_id, "units:", _data["units"])
        response = self.session.post(self.data_url, headers=self.headers,
                                     data=json.dumps(_data))
        assert response.status_code == 200

    def get_frame(self, frame_index=-1):
        if frame_index==-1:
            _data = {}
        else:
            _data = self.gen_data()
        _data["frame_index"] = frame_index
        response = self.session.get(self.canbus_url, headers=self.headers,
                                    params=_data)
        try:
            assert response.status_code == 200
        except:
            #print("got odd response code: ", response.status_code, "on params:", _data)
            return None
        response = response.json()
        try:
            if response["test_run_id"] != self.test_run_id:
                self.test_run_id = response["test_run_id"]
                self.last_frame = -1
                print("new test run ID is: ", self.test_run_id)
        except:
            print("got empty response:", response)
            return None
        return response

    def post_frame(self, frame):
        if self.test_run_id is None:
            return
        _data = self.gen_data()
        command_code = frame.data[0] if len(frame.data) > 0 else None
        _data["frames"] = [{"address": [0, 0], "command_code": command_code,
                            "frame_data": frame.data[1:],
                            "explanation": frame.explanation,
                            "written": True}]
        response = self.session.post(self.canbus_url, headers=self.headers,
                                     data=json.dumps(_data))
        assert response.status_code == 200

    def post_status(self, _card_status):
        _data = {"gateway_name": COMMON_SETTINGS["HARDWARENAME"],
                 "status": _card_status}
        response = self.session.post(self.status_url, headers=self.headers,
                                     data=json.dumps(_data))
        assert response.status_code == 200

    def update_frame(self, new_vals):
        if not self.test_run_id:
            return
        _data = self.gen_data()
        _data.update(new_vals)
        response = self.session.put(self.canbus_url, headers=self.headers,
                                    data=json.dumps(_data))
        assert response.status_code == 200

    def send_status(self):
        while True:
            if self.card.unplugged:
                _card_status = ["Motor unresponsive"]
            else:
                _card_status = self.card.status
            if self.prev_status != _card_status:
                # the next one is the same as this, continue
                self.post_status(_card_status)
                self.prev_status = _card_status
            sleep(BREATH_TIME)

    def sync_device(self):
        while True:
            sleep(BREATH_TIME)
            if self.card.unplugged:
                return
            if self.sync_on:
                self.card.acknowledge()

    def log_threads(self):
        while True:
            sleep(BREATH_TIME)
            # post the logs
            for log in self.card.logs:
                self.post_log(log)
            self.card.logs = []

    def canbus_threads(self):
        while True:
            sleep(BREATH_TIME)
            # post the sent/received CAN Frames
            if self.canbus_on:
                for frame in self.card.frames_list:
                    self.post_frame(frame)
                self.card.frames_list = []
                incoming_frame = self.get_frame()
                if incoming_frame is None:
                    continue
                frames_to_write = []
                if "written" not in incoming_frame.keys():
                   incoming_frame["written"] = False
                if "frame_index" not in incoming_frame.keys():
                   print("got frame missing index!")
                   continue
                if incoming_frame["frame_index"] > self.last_frame and "written" in incoming_frame.keys():
                    print("incoming frame index:", incoming_frame["frame_index"])
                    # get all frames between the two
                    for i in range(self.last_frame + 1, incoming_frame["frame_index"]):
                        between_frame = self.get_frame(frame_index=i)
                        try:
                            if "written" not in between_frame.keys():
                                between_frame["written"] = True
                            if not between_frame["written"]:                      
                                frames_to_write.append(between_frame)
                        except:
                            print("had trouble with frame: ", between_frame, "id: ", i)
                    if not incoming_frame["written"]:
                        print("frames to write: ", incoming_frame, "last frame: ", self.last_frame)
                        frames_to_write.append(incoming_frame)
                    self.last_frame = incoming_frame["frame_index"]
                for write_frame in frames_to_write:
                    print("address is: ", write_frame["address"], "keys:", write_frame.keys())
                    address = (write_frame["address"][0] << 8) + write_frame["address"][1]
                    data = [write_frame["command_code"]]+ write_frame["frame_data"]
                    xmit_frame = CanFrame(id=address, data=data)
                    self.card.xmit(xmit_frame)
                    write_frame["explanation"] = self.card.frames_list[-1].explanation
                    write_frame["written"] = True
                    self.update_frame(write_frame)

    def run_test(self):
        """
        State machine to handle
        """
        state = MotorState.IDLE
        while True:
            sleep(BREATH_TIME)
            #if len(self.test_order.keys()) != 0:
            #    print("run test keys:", self.test_order.keys(), self.config_parts, set(self.config_parts).issubset(self.test_order.keys()))
            if state == MotorState.IDLE and \
                    not set(self.config_parts).issubset(self.test_order.keys()):
                self.sync_on = False
            elif state == MotorState.IDLE:
                self.sync_on = True
                # set up parameters once
                if self.test_order['trace'] == "poll":
                    for parameter in self.test_order['properties']:
                        _ = self.card.property_getter(parameter)
                state = MotorState.HOMING
            if self.card.unplugged:
                return
            if state == MotorState.HOMING:
                self.card.move(0)
                if self.card.property_getter("actual_position")==0:
                    self.start_time = time()
                    self.canbus_on = False
                    state = MotorState.MOVING
            elif state == MotorState.MOVING:
                self.card.move(self.test_order["motor_end_position"])
                print("doing trace")
                self.sync_on = False
                self.data_points = self.card.do_trace(max_counts=10000,
                                                      max_time=self.test_order['time_window'],
                                                      properties=self.test_order['properties'],
                                                      sync=self.test_order['trace']=="poll")
                # update the test to complete, then return to idle
                self.test_run_id = self.test_order['test_run_id']
                self.post_data()
                self.test_order = {}
                self.data_points = []
                state = MotorState.IDLE
                self.canbus_on = True
                self.sync_on = False

ANGULAR_FORM = {"schema": SCHEMA_DICT,
                "form": FORM_DICT,
                "defaults": [["select", "poll"]]}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.argv.append("")
    if sys.argv[1] == "-t":
        print("testing, not client mode")
        test_api()
    else:
        run_gateway()
