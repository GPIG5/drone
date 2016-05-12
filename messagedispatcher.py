from asyncio import Queue, coroutine
import messages

class Messagedispatcher:
    def __init__(self, communicator):
        self.communicator = communicator
        self.messages = {
            "direct": {
                "status": {
                    "class": messages.StatusDirect,
                    "queue": Queue()
                },
                "pinor": {
                    "class": messages.PinorDirect,
                    "queue": Queue()
                }
            },
            "mesh": {
                "status": {
                    "class": messages.StatusMesh,
                    "queue": Queue()
                },
                "pinor": {
                    "class": messages.PinorMesh,
                    "queue": Queue()
                }
            }
        }
    @coroutine
    def wait_for_message(self, *types):
        x = self.messages
        for i in types:
            x = x[i]
        q = x["queue"]
        return (yield from q.get())
    @coroutine
    def startup(self):
        while True:
            msg = yield from self.communicator.receive()
            x = self.messages
            x = x[msg["type"]]
            x = x[msg["data"]["datatype"]]
            q = x["queue"]
            c = x["class"]
            yield from q.put(c.from_json(msg))
