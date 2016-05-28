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
    def __init__(self, next, telemetry, config, communicator, drone_speed):
        Layer.__init__(self, next)
        self.telemetry = telemetry
        self.config = config
        self.communicator = communicator
        self.drone_speed = drone_speed
        self.state = State.normal

    def execute_layer(self, current_output):

        op = current_output
        init_loc = self.telemetry.get_initial_location()
        current_location = self.telemetry.get_location()
        current_battery = self.telemetry.get_battery()

        if self.state == State.normal:

            # Checks whether we have enough battery to return home (+ safety margin of 150 seconds)
            if (init_loc.distance_to(current_location) / self.drone_speed) + 150 > current_battery:
                self.state = State.going_home
                print("LOW BATTERY")
            else:
                op = Layer.execute_layer(self, op)

        if self.state == State.going_home:
            if current_location.distance_to(init_loc) < 10:
                b1 = io.BytesIO()
                # b2 = io.StringIO()
                tar = tarfile.open(mode = "w|", fileobj=b1)
                tar.add("data/" + self.config["uuid"])
                tar.close()
                b64_encoded = base64.b64encode(b1.getvalue())
                self.communicator.send_message(UploadDirect(self.config["uuid"], b64_encoded))
                self.telemetry.recharge_battery()
                self.state == State.normal
            else:
                op.move = self.telemetry.get_initial_location()

        return op
