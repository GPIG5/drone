import communicator
import asyncio

@asyncio.coroutine
def main(host):
    c = communicator.Communicator()
    yield from c.connect(host)
    print("connected")
    #yield from c.send("hello")
    #print("sent")
    m = yield from c.receive()
    print(m)

loop = asyncio.get_event_loop()
loop.run_until_complete(main("144.32.178.55"))
loop.close()
