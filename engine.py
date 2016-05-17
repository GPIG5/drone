import asyncio
from geopy.distance import great_circle
from math import acos, cos, pi, sin
from point import Point

class Engine:
    def __init__(self, config, telemetry, navigator, speed = 2):
        self.telemetry = telemetry
        self.navigator = navigator
        self.speed = config.getint('speed')
        self.travel_time = config.getint('travel_time')

    @asyncio.coroutine
    def startup(self):
        while True:
            current_location = self.telemetry.get_location().p
            target_location = self.navigator.get_current_target().p

            target_distance = great_circle(current_location, target_location).meters
            travel_distance = self.speed / self.travel_time

            if (target_distance != 0):
                if (sin(target_location.longitude - current_location.longitude) < 0):
                    bearing = acos((
                        sin(target_location.latitude) - sin(current_location.latitude) * cos(target_distance)) /
                        (sin(target_distance) * cos(current_location.latitude)))
                else:
                    bearing = 2 * pi - acos((
                        sin(target_location.latitude) - sin(current_location.latitude) * cos(target_distance)) /
                        (sin(target_distance) * cos(current_location.latitude)))

                travel_destination = great_circle(meters=travel_distance).destination(current_location, bearing)

                self.telemetry.set_location(Point(travel_destination))

            yield from asyncio.sleep(self.travel_time)
