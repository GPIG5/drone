import asyncio
from geopy.distance import great_circle
import math
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

            target_distance = great_circle(current_location, target_location).meters
            travel_distance = self.speed * self.travel_time
            travel_distance = target_distance if target_distance < travel_distance else travel_distance

            if (target_distance != 0):

                bearing = current_location.bearing_to_point(target_location)

                travel_destination = great_circle(meters=travel_distance).destination(current_location, bearing)
                travel_destination.altitude = target_location.altitude

                # print('Location: ' + str(current_location) + ' Bearing: ' + str(bearing))
                # print('Destination: ' + str(travel_destination) + ' Target: ' + str(target_location))

                yield from self.telemetry.set_location(Point(travel_destination))

            yield from asyncio.sleep(self.travel_time)
