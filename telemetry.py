from ast import literal_eval as make_tuple
import asyncio

from messages import StatusDirect, StatusMesh
from point import Point

class Telemetry:
    def __init__(self, config, communicator):
        self.communicator = communicator

        self.uuid = config.get('uuid')
        self.battery_size = config.getfloat('battery_size')
        self.initial_location = Point(*make_tuple(config.get('start_location')))
        self.location = self.initial_location
        self.location_lock = asyncio.Lock()
        self.start_time = 0

    @asyncio.coroutine
    def initialise(self):
        self.start_time = asyncio.get_event_loop().time()

    @asyncio.coroutine
    def startup(self):
        while True:
            location = self.get_location()
            battery = self.get_battery()

            env_status = StatusDirect(self.uuid, location, battery)
            mesh_status = StatusMesh(self.uuid, self.uuid, location, battery)

            yield from self.communicator.send(env_status.to_json())
            yield from self.communicator.send(mesh_status.to_json())

            yield from asyncio.sleep(1)

    def get_location(self):
        return self.location

    @asyncio.coroutine
    def set_location(self, new_location : Point):
        with (yield from self.location_lock):
            self.location = new_location

    def get_initial_battery(self):
        return self.battery_size

    def get_initial_location(self):
        return self.initial_location

    def get_battery(self):
        current_time = asyncio.get_event_loop().time()
        elapsed_time = current_time - self.start_time

        return self.battery_size - elapsed_time

    def recharge_battery(self):
        self.initialise()
