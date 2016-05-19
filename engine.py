import asyncio
from geopy.distance import great_circle
from math import acos, cos, pi, sin
from point import Point

class Engine:
    def __init__(self, config, telemetry, navigator):
        self.telemetry = telemetry
        self.navigator = navigator
        self.speed = config.getint('speed')
        self.travel_time = config.getint('travel_time')

    @asyncio.coroutine
    def startup(self):
        while True:
            current_location = self.telemetry.get_location()
            target_location = self.navigator.get_current_target()

            target_distance = great_circle(current_location, target_location).kilometers
            travel_distance = self.speed / self.travel_time

            if (target_distance != 0):
                # algorithm from http://williams.best.vwh.net/avform.htm#Crs
                if (sin(target_location.longitude - current_location.longitude) < 0):
                    bearing = acos((
                        sin(target_location.latitude) - sin(current_location.latitude) * cos(target_distance)) /
                        (sin(target_distance) * cos(current_location.latitude)))
                else:
                    bearing = 2 * pi - acos((
                        sin(target_location.latitude) - sin(current_location.latitude) * cos(target_distance)) /
                        (sin(target_distance) * cos(current_location.latitude)))

                travel_destination = great_circle(meters=travel_distance).destination(current_location, bearing)

                yield from self.telemetry.set_location(Point(travel_destination))

            yield from asyncio.sleep(self.travel_time)
