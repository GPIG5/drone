import asyncio
import time
import configparser
from enum import Enum
import datastore
from reactor import Reactor


class Navigator:
    def __init__(self, messagedispatcher, telemetry):
        self.messagedispatcher = messagedispatcher
        self.reactor = Reactor(telemetry)

    @asyncio.coroutine
    def startup(self):
        while True:
            self.reactor.run()
            yield from asyncio.sleep(1)