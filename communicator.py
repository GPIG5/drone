import asyncio
import json
import struct

from messages import DirectMessage

class Communicator:
    def __init__(self, drone):
        self.drone = drone
        self.config = self.drone.getConfig('communicator')
        self.host = self.config.get('host')
        self.port = self.config.getInt('port')

    async def initialise():
        await connect(self.host, self.port)
        hello = DirectMessage(self.drone.getUUID())
        await send(hello)

	async def connect(self, host, port):
		reader, writer = await asyncio.open_connection(host, port)
		self.reader = reader
		self.writer = writer

	async def send(self, data):
		encoded = json.dumps(data).encode('utf-8')
		self.writer.write(struct.pack("!L", len(encoded)))
		self.writer.write(encoded)

	async def receive(self):
		unencoded_size = await self.reader.readexactly(4)
		encoded_size = struct.unpack("!L", unencoded_size)[0]
		unencoded_data = await self.reader.readexactly(encoded_size)
		encoded_data = json.loads(unencoded_data.decode())
		return encoded_data
