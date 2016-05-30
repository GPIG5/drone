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
    def __init__(self, next, config, telemetry, communicator, engine):
        Layer.__init__(self, next)
        self.telemetry = telemetry
        self.communicator = communicator
        self.state = State.normal
        self.engine = engine
        self.drone_speed = config['speed']

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
            init_loc = self.telemetry.get_initial_location()
            current_location = self.telemetry.get_location()
            current_battery = self.telemetry.get_battery()

            # Checks whether we have enough battery to return home (+ safety margin of 150 seconds)
            if (init_loc.distance_to(current_location) / self.drone_speed) + 150 > self.telemetry.get_battery():
                self.state = State.going_home
                print("LOW BATTERY")
            if self.state == State.going_home:
                print("at home")
                if self.telemetry.get_location().distance_to(self.telemetry.get_initial_location()) < 10:
                    #wait ten seconds for battery replacement
                    print("REPLACING BATTERY")
                    asyncio.sleep(10)
                    self.telemetry.recharge_battery()
                    self.state = State.normal
                    print("BATTERY REPLACED")
            yield from asyncio.sleep(1)
