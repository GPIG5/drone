import asyncio
import bisect

class MeshController:
    def __init__(self, message_dispatcher, drone, communicator, max_messages = 3):
        self.message_dispatcher = message_dispatcher
        self.drone = drone
        self.origin_map = {}
        self.communicator = communicator
        self.max_messages = max_messages
    @asyncio.coroutine
    def startup(self):
        while True:
            msg = yield from self.message_dispatcher.get_mesh_message()
            ts = msg.timestamp
            origin = msg.origin
            if self.add_message(ts, origin):
                msg.uuid = self.drone.getUUID()
                self.communicator.send_message(msg)
    def add_message(self, ts, origin):
        if origin in self.origin_map:
            l = self.origin_map[origin]
            if ts in l:
                return False
            elif len(l) < max_messages:
                bisect.insort(l, ts)
                return True
            elif ts < l[0]:
                return False
            else:
                bisect.insort(l, ts)
                self.origin_map[origin] = l[1:]
                return True
        else:
            self.origin_map[origin] = [ts]
            return True
