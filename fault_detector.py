from layer import *
import asyncio
import time
import math
from enum import Enum

class State(Enum):
    normal = 0
    going_home = 1

class FaultDetector(Layer):
    def __init__(self, next, telemetry):
        Layer.__init__(self, next)
        self.telemetry = telemetry
        self.state = State.normal

    def execute_layer(self, current_output):
        op = current_output
        if self.state == State.going_home:
            op.move = self.telemetry.get_initial_location()
        elif self.state == State.normal:
            op = Layer.execute_layer(self, op)
        else:
            raise NotImplementedError()
        return op

    @asyncio.coroutine
    def startup(self):
        ctime = time.time()
        cbattery = self.telemetry.get_battery()
        cbattery_id = 0
        while True:
            last_time = ctime
            last_battery = cbattery
            last_battery_id = cbattery_id
            yield from asyncio.sleep(10)
            ctime = time.time()
            cbattery = self.telemetry.get_battery()
            cbattery_id = self.telemetry.get_battery_id()
            if last_battery_id != cbattery_id:
                self.state = State.normal
                print("BATTERY FAULT REMOVED")
                continue
            pchange = ((math.fabs((ctime - last_time) - (cbattery - last_battery)) / 20) - 1) * 100
            if pchange > 10:
                print("BATTERY FAULT DETECTED")
                print(str(pchange) + " percentage error")
                self.state = State.going_home
