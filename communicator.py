import asyncio
import json
import struct

from messages import DirectMessage

class Communicator:
    def __init__(self, config):
        self.host = config.get('host')
        self.port = config.getint('port')
        self.uuid = config.get('uuid')

    @asyncio.coroutine
    def initialise(self):
        yield from self.connect()
        hello = DirectMessage(self.uuid)
        yield from self.send(hello.to_json())

    @asyncio.coroutine
    def connect(self):
        reader, writer = yield from asyncio.open_connection(self.host, self.port)
        self.reader = reader
        self.writer = writer

    @asyncio.coroutine
    def send(self, data):
        encoded = json.dumps(data).encode('utf-8')
        self.writer.write(struct.pack("!L", len(encoded)))
        self.writer.write(encoded)

    @asyncio.coroutine
    def receive(self):
        unencoded_size = yield from self.reader.readexactly(4)
        encoded_size = struct.unpack("!L", unencoded_size)[0]
        unencoded_data = yield from self.reader.readexactly(encoded_size)
        encoded_data = json.loads(unencoded_data.decode())
        return encoded_data
