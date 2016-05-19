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
            travel_distance = self.speed / self.travel_time
            travel_distance = target_distance if target_distance < travel_distance else travel_distance

            if (target_distance != 0):
                # algorithm from http://williams.best.vwh.net/avform.htm#Crs

                lat1 = math.radians(current_location.latitude)
                lat2 = math.radians(target_location.latitude)

                diffLong = math.radians(target_location.longitude - current_location.longitude)
                x = math.sin(diffLong) * math.cos(lat2)
                y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))

                initial_bearing = math.atan2(x, y)
                initial_bearing = math.degrees(initial_bearing)
                bearing = (initial_bearing + 360) % 360

                travel_destination = great_circle(meters=travel_distance).destination(current_location, bearing)
                travel_destination.altitude = target_location.altitude

                print(current_location)
                print(bearing)
                print(travel_destination)
                print(target_location)

                yield from self.telemetry.set_location(Point(travel_destination))

            yield from asyncio.sleep(self.travel_time)
