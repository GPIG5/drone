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
    normal = 0
    uploading = 1

class ImageUploader(Layer):
    def __init__(self, next, telemetry, detection, communicator):
        Layer.__init__(self, next)
        self.telemetry = telemetry
        self.detection = detection
        self.communicator = communicator
        self.last_upload_time = self.telemetry.get_start_time()
        self.state = State.normal

    def execute_layer(self, current_output):
        op = current_output
        if self.state == State.uploading:
            op.move = self.telemetry.get_initial_location()
        elif self.state == State.normal:
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
                if (time.time() - self.last_upload_time) > 10:
                    self.state = State.uploading
                    print("UPLOADING")
                    op = yield from self.readfiles(self.detection.get_data_folder())
                    yield from self.communicator.send_message(messages.UploadDirect(
                        self.telemetry.uuid,
                        op
                    ))
                    self.state = State.normal
                    print("FINISHED UPLOADING")
                    self.last_upload_time = time.time()
            yield from asyncio.sleep(1)
