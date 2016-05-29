import asyncio
import bisect

class MeshController:
    def __init__(self, config, message_dispatcher, communicator, **kwargs):
        self.message_dispatcher = message_dispatcher
        self.uuid = config.get('uuid')
        self.origin_map = {}
        self.communicator = communicator
        self.max_messages = int(config.get('max_messages'))
    @asyncio.coroutine
    def startup(self):
        while True:
            msg = yield from self.message_dispatcher.get_mesh_message()
            if msg.uuid == self.uuid or msg.origin == self.uuid:
                continue
            ts = msg.timestamp
            origin = msg.origin
            if self.add_message(ts, origin):
                msg.uuid = self.uuid
                self.communicator.send_message(msg)
    def add_message(self, ts, origin):
        if origin in self.origin_map:
            l = self.origin_map[origin]
            if ts in l:
                return False
            elif len(l) < self.max_messages:
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
