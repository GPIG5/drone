from layer import *
from enum import Enum
import time
import asyncio
import aiofiles
import os
import os.path
import base64
import messages

class State(Enum):
    ready = 0
    busy = 1

class PitStop(Layer):
    def __init__(self, next, telemetry, detection, communicator, config):
        Layer.__init__(self, next)
        self.telemetry = telemetry
        self.detection = detection
        self.communicator = communicator
        self.last_upload_time = self.telemetry.get_start_time()
        self.state = State.ready
        self.uuid = config['DEFAULT']['uuid']

    def execute_layer(self, current_output):
        op = current_output
        if self.state == State.busy:
            op.move = self.telemetry.get_initial_location()
        elif self.state == State.ready:
            op = Layer.execute_layer(self, op)
        else:
            raise NotImplementedError()
        return op

    @asyncio.coroutine
    def readfiles(self, path):
        op = {}
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                fl = yield from aiofiles.open(os.path.join(path, f), mode='rb')
                try:
                    contents = yield from fl.read()
                finally:
                    yield from fl.close()
                op[f] = base64.b64encode(contents).decode('utf-8')
            else:
                op[f] = yield from self.readfiles(os.path.join(path, f))
        return op

    @asyncio.coroutine
    def startup(self):
        while True:
            if self.telemetry.get_location().distance_to(self.telemetry.get_initial_location()) < 10:
                if (time.time() - self.last_upload_time) > 600:
                    self.last_upload_time = time.time()
                    self.state = State.busy
                    print("PERFORMING MAINTAINENCE")
                    self.telemetry.recharge_battery()
                    op = yield from self.readfiles(self.detection.get_data_folder())
                    yield from self.communicator.send_message(messages.UploadDirect(
                        self.uuid,
                        op
                    ))
                    self.state = State.ready
                    print("FINISHED MAINTAINENCE")
            yield from asyncio.sleep(1)
