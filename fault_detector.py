from layer import *

class FaultDetector(Layer):
    def __init__(self, next):
        Layer.__init__(self, next)

    def execute_layer(self, current_output):
        op = current_output
        op = Layer.execute_layer(self, op)
        return op

    @asyncio.coroutine
    def startup(self):
        while True:
            asyncio.sleep(4)
