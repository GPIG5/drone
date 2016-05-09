import Communicator
import asyncio

@asyncio.coroutine
def main(host):
	c = Communicator.Communicator()
	yield from c.connect(host)
	print("connected")
	yield from c.send("hello")
	print("sent")
	m = yield from c.receive()
	print(m)

loop = asyncio.get_event_loop()
loop.run_until_complete(main("10.240.149.164"))
loop.close()
