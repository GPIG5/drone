from layer import *
import tarfile
import time
import base64
import io
from messages import UploadDirect

class BatteryLifeChecker(Layer):
    def __init__(self, next, telemetry, config, communicator):
        Layer.__init__(self, next)
        self.telemetry = telemetry
        self.config = config
        self.communicator = communicator
    def execute_layer(self, current_output):
        op = current_output
        if self.telemetry.get_battery() < (self.telemetry.get_initial_battery() / 2) + 240:
            print("LOW BATTERY")
            if self.telemetry.get_location().distance_to(
                self.telemetry.get_initial_location()
            ) < 10:
                b1 = io.BytesIO()
                b2 = io.StringIO()
                tar = tarfile.open(mode = "w|", fileobj=b1)
                tar.add("data/" + self.config["uuid"])
                tar.close()
                base64.encode(b1, b2)
                self.communicator.send_message(UploadDirect(self.config["uuid"], b2.getvalue()))
                self.telemetry.recharge_battery()
            else:
                op.move = self.telemetry.get_initial_location()
        else:
            op = Layer.execute_layer(self, op)
        return op
