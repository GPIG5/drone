from ast import literal_eval as make_tuple
import asyncio

from messages import StatusDirect, StatusMesh
from point import Point

class Telemetry:
    def __init__(self, config, communicator):
        self.communicator = communicator

        self.uuid = config.get('uuid')
        self.batterySize = config.getfloat('battery_size')
        self.location = Point(*make_tuple(config.get('start_location')))
        self.locationLock = asyncio.Lock()
        self.startTime = 0

    @asyncio.coroutine
    def initialise(self):
        self.startTime = asyncio.get_event_loop().time()

    @asyncio.coroutine
    def startup(self):
        while True:
            location = self.getLocation()
            battery = self.getBattery()

            envStatus = StatusDirect(self.uuid, location, battery)
            meshStatus = StatusMesh(self.uuid, self.uuid, location, battery)

            yield from self.communicator.send(envStatus.to_json())
            yield from self.communicator.send(meshStatus.to_json())

            yield from asyncio.sleep(1)

    def getLocation(self):
        return self.location

    @asyncio.coroutine
    def setLocation(self, newLocation : Point):
        with (yield from locationLock):
            self.location = newLocation

    def getBattery(self):
        currentTime = asyncio.get_event_loop().time()
        elapsedTime = currentTime - self.startTime

        return self.batterySize - elapsedTime

    def rechargeBattery(self):
        initialise()
