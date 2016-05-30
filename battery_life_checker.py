from enum import Enum

import messages
from layer import *
import tarfile
import time
import base64
import io
from messages import UploadDirect

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
    def life_startup(self):
        while True:
            if self.state == State.normal:
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
            yield from asyncio.sleep(1)

    @asyncio.coroutine
    def fault_startup(self):
        ctime = time.time()
        cbattery = self.telemetry.get_battery()
        while True:
            last_time = ctime
            last_battery = cbattery
            yield from asyncio.sleep(10)
            ctime = time.time()
            cbattery = self.telemetry.get_battery()
            if self.state == State.normal:
                pchange = ((math.fabs((ctime - last_time) - (cbattery - last_battery)) / 20) - 1) * 100
                if pchange > 10:
                    print("BATTERY FAULT DETECTED")
                    print(str(pchange) + " percentage error")
                    self.bad_state()
