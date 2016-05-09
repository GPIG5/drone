import asyncio
import json
import struct

class Communicator:
	@asyncio.coroutine
	def connect(self, host):
		reader, writer = yield from asyncio.open_connection(host, 5555)
		self.reader = reader
		self.writer = writer
	@asyncio.coroutine
	def send(self, data):
		encoded = json.dumps(data).encode()
		yield from self.writer.write(struct.pack("!L", len(encoded)))
		yield from self.writer.write(encoded)
	@asyncio.coroutine
	def receive(self):
		unencoded_size = yield from self.reader.readexactly(4)
		encoded_size = struct.unpack("!L", unencoded_size)
		unencoded_data = yield from self.reader.readexactly(encoded_size)
		encoded_data = json.loads(unencoded_data.decode())
		return encoded_data
