from enum import Enum

import messages
from layer import *
import tarfile
import time
import base64
import io
from messages import UploadDirect
import asyncio

class State(Enum):
    normal = 0
    going_home = 1

class BatteryLifeChecker(Layer):
    def __init__(self, next, telemetry, communicator, engine):
        Layer.__init__(self, next)
        self.telemetry = telemetry
        self.communicator = communicator
        self.state = State.normal
        self.engine = engine

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
        while True:
            if (self.telemetry.get_initial_battery() / 2) + 150 > self.telemetry.get_battery():
                self.state = State.going_home
                print("LOW BATTERY")
            if self.state == State.going_home:
                if self.telemetry.get_location().distance_to(self.telemetry.get_initial_location()) < 10:
                    #wait ten seconds for battery replacement
                    print("REPLACING BATTERY")
                    asyncio.sleep(10)
                    self.telemetry.recharge_battery()
                    self.state = State.normal
                    print("BATTERY REPLACED")
            asyncio.sleep(1)
