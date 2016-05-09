from Communicator import *

@asyncio.coroutine
def main(host):
	c = Communicator()
	yield from c.connect(host)
	yield from c.send({"test": "hello"})
	m = yield from c.receive()
	print(m)

loop = asyncio.get_event_loop()
loop.run_until_complete(main("lol"))
loop.close()
