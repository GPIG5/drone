import asyncio
import time
import configparser
from enum import Enum
import datastore
from reactor import Reactor
from point import Point


class Navigator:
    def __init__(self, config, data_store, telemetry, messagedispatcher):
        self.messagedispatcher = messagedispatcher
        self.reactor = Reactor(config, data_store, telemetry)
        self.current_target = Point(
            longitude = telemetry.get_location().longitude + 10,
            latitude = telemetry.get_location().latitude,
            altitude = telemetry.get_location().altitude
        )

    @asyncio.coroutine
    def startup(self):
        while True:
            action = self.reactor.run()
            if action.move != None:
                self.current_target = action.move
            yield from asyncio.sleep(1)

    def get_current_target(self):
        return self.current_target




