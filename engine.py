import asyncio
from geopy.distance import great_circle
import math
from point import Point

class Engine:
    def __init__(self, config, **kwargs):
        self.speed = config.getint('speed')
        self.travel_time = config.getint('travel_time')
        self.current_target = None
        self.location = None

    def get_speed(self):
        return self.speed

    def get_current_target(self):
        if self.current_target is None:
            raise Exception()
        return self.current_target

    def set_current_target(self, ct):
        self.current_target = ct

    def get_location(self):
        if self.location is None:
            raise Exception()
        return self.location

    def set_location(self, ct):
        self.location = ct

    def get_travel_time(self):
        return self.travel_time

    @asyncio.coroutine
    def startup(self):
        while True:
            target_location = self.get_current_target()
            if target_location is None:
                raise Exception("none target location")
            current_location = self.get_location()
            target_distance = great_circle(current_location, target_location).meters
            travel_distance = self.speed * self.get_travel_time()
            travel_distance = target_distance if target_distance < travel_distance else travel_distance

            if (target_distance != 0):

                bearing = current_location.bearing_to_point(target_location)

                travel_destination = great_circle(meters=travel_distance).destination(current_location, bearing)
                travel_destination.altitude = target_location.altitude

                # print('Location: ' + str(current_location) + ' Bearing: ' + str(bearing))
                # print('Destination: ' + str(travel_destination) + ' Target: ' + str(target_location))

                self.set_location(Point(travel_destination))

            yield from asyncio.sleep(self.get_travel_time())
