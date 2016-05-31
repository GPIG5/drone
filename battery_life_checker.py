from enum import Enum

import messages
from layer import *
import tarfile
import time
import base64
import io
from messages import UploadDirect
import asyncio
import math

class State(Enum):
    normal = 0
    going_home = 1

class BatteryLifeChecker(Layer):
    def __init__(self, next, telemetry, drone_speed):
        Layer.__init__(self, next)
        self.telemetry = telemetry
        self.drone_speed = drone_speed
        self.state = State.normal
        self.bad_battery_id = 0

    def execute_layer(self, current_output):
        op = current_output
        if self.state == State.going_home:
            op.move = self.telemetry.get_initial_location()
        elif self.state == State.normal:
            op = Layer.execute_layer(self, op)
        else:
            raise NotImplementedError()
        return op

    def bad_state(self):
        self.state = State.going_home
        self.bad_battery_id = self.telemetry.get_battery_id()

    @asyncio.coroutine
    def startup(self):
        yield from asyncio.gather(self.life_startup(), self.fault_startup(), self.battery_change_detector_startup())

    @asyncio.coroutine
    def life_startup(self):
        while True:
            if self.state == State.normal:
                init_loc = self.telemetry.get_initial_location()
                current_location = self.telemetry.get_location()
                current_battery = self.telemetry.get_battery()
                if (init_loc.distance_to(current_location) / self.drone_speed) + 150 > current_battery:
                    self.bad_state()
                    print("LOW BATTERY")
            yield from asyncio.sleep(1)

    @asyncio.coroutine
    def battery_change_detector_startup(self):
        while True:
            if self.state == State.going_home and self.bad_battery_id != self.telemetry.get_battery_id():
                #battery changed
                self.state = State.normal
            yield from asyncio.sleep(5)

    @asyncio.coroutine
    def fault_startup(self):
        init = True
        last_time = time.time()
        last_battery = self.telemetry.get_battery()
        while True:
            ctime = time.time()
            cbattery = self.telemetry.get_battery()
            if self.state == State.normal:
                if init:
                    init = False
                else:
                    pchange = (
                        math.fabs(
                            float(
                                ctime - last_time
                            ) - float(
                                last_battery - cbattery
                            )
                        ) / float(
                            self.telemetry.get_initial_battery()
                        )
                    ) * 100.0
                    if pchange > 20:
                        print("BATTERY FAULT DETECTED")
                        print(str(pchange) + " percentage error")
                        self.bad_state()
            else:
                init = True
            last_time = ctime
            last_battery = cbattery
            yield from asyncio.sleep(5)
