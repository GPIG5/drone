import asyncio

from messages import PinorMesh

class Detection:
	def __init__(self, config, communicator, messagedispatcher):
        self.uuid = config.get('uuid')
        self.communicator = communicator
		self.messagedispatcher = messagedispatcher
        self.pinor = []

	@asyncio.coroutine
	def startup(self):
		while True:
            msg = yield from self.messagedispatcher.wait_for_message("direct", "pinor").to_json()
            pinor = (time.time(), msg['data']['pinor'])
            img = msg['data']['img']
            self.pinor.append(pinor)
            yield from self.communicator.send(PinorMesh(self.uuid, self.uuid, pinor).to_json())

    def get_pinor():
        return self.pinor
