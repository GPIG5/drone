import asyncio
import time
import configparser
from enum import Enum
import datastore
from reactor import Reactor


class Navigator:
    def __init__(self, config, data_store, telemetry, messagedispatcher):
        self.messagedispatcher = messagedispatcher
        self.reactor = Reactor(config, data_store, telemetry)

    @asyncio.coroutine
    def startup(self):
        while True:
            self.reactor.run()
            yield from asyncio.sleep(1)