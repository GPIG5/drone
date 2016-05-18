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
                },
                "return": {
                    "class": messages.ReturnMesh,
                    "queue": Queue()
                },
                "deploy": {
                    "class": messages.DeployMesh,
                    "queue": Queue()
                }
            }
        }
        self.mesh_queue = Queue()
    @coroutine
    def wait_for_message(self, *types):
        x = self.messages
        for i in types:
            x = x[i]
        q = x["queue"]
        return (yield from q.get())
    @coroutine
    def get_mesh_message(self):
        return (yield from self.mesh_queue.get())
    @coroutine
    def startup(self):
        while True:
            msg = yield from self.communicator.receive()
            if msg["type"] == "mesh":
                yield from self.mesh_queue.put(msg)
            x = self.messages
            x = x[msg["type"]]
            x = x[msg["data"]["datatype"]]
            q = x["queue"]
            c = x["class"]
            yield from q.put(c.from_json(msg))
