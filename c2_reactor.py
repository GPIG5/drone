from layer import *
import asyncio

class C2Reactor(Layer):
    def __init__(self, next, data_store, message_dispatcher, telemetry):
        Layer.__init__(self, next)
        self.ts = 0
        self.returning = False
        self.current_space = None
        self.message_dispatcher = message_dispatcher
        self.telemetry = telemetry
        self.data_store = data_store

    def execute_layer(self, current_output):
        op = Layer.execute_layer(self, current_output)
        if self.returning:
            op.move = self.telemetry.get_initial_location()
            if hasattr(current_output.move, 'simple_string'):
                op.move_info = "C2 INSTRUCTION: " + op.move.simple_string()
            else:
                op.move_info = "C2 INSTRUCTION: "
        return op

    @asyncio.coroutine
    def startup(self):
        yield from asyncio.gather(self.returnjob(), self.deployjob())

    @asyncio.coroutine
    def returnjob(self):
        while True:
            msg = yield from self.message_dispatcher.wait_for_message("mesh", "return")
            if self.ts < msg.timestamp:
                self.returning = True

    @asyncio.coroutine
    def deployjob(self):
        while True:
            msg = yield from self.message_dispatcher.wait_for_message("mesh", "deploy")
            if self.ts < msg.timestamp:
                self.returning = False
                self.current_space = msg.space
                self.data_store.set_search_space(self.current_space)

    def get_current_space(self):
        return self.current_space
