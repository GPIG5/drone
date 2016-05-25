from ast import literal_eval as make_tuple
import asyncio

from messages import StatusDirect, StatusMesh
from point import Point
import random


class Telemetry:
    def __init__(self, config, communicator, defects, travel_time):
        self.communicator = communicator
        self.leaky_battery = ('True' == defects['leaky_battery'])
        if self.leaky_battery:
            print("The battery is set to leak")

        self.uuid = config.get('uuid')
        self.real_battery_size = config.getfloat('battery_size')
        self.battery_size = self.real_battery_size
        self.initial_location = Point(*make_tuple(config.get('start_location')))
        self.location = self.initial_location
        self.location_lock = asyncio.Lock()
        self.start_time = 0
        self.travel_time = travel_time

    @asyncio.coroutine
    def initialise(self):
        self.start_time = asyncio.get_event_loop().time()

    @asyncio.coroutine
    def startup(self):
        while True:
            if self.leaky_battery:
                if random.randint(0, 100) < 2:
                    self.battery_size = self.battery_size / 2
            if (self.get_battery() <= 0):
                raise "OUT OF BATTERY"

            location = self.get_location()
            battery = self.get_battery()

            env_status = StatusDirect(self.uuid, location, battery)
            mesh_status = StatusMesh(self.uuid, self.uuid, location, battery)

            yield from self.communicator.send(env_status.to_json())
            yield from self.communicator.send(mesh_status.to_json())

            yield from asyncio.sleep(self.travel_time)

    def get_location(self):
        return self.location

    @asyncio.coroutine
    def set_location(self, new_location: Point):
        with (yield from self.location_lock):
            if new_location is None:
                raise "lol"
            if (self.get_battery() > 0):
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
        self.start_time = asyncio.get_event_loop().time()
        self.battery_size = self.real_battery_size
