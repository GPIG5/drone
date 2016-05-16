import asyncio
import math
from point import Point

class Engine:
    def __init__(self, telemetry, navigator, speed = 2):
        self.telemetry = telemetry
        self.navigator = navigator
        self.speed = 2

    @asyncio.coroutine
    def startup(self):
        while True:
            t = self.navigator.get_current_target()
            loc = self.telemetry.get_location()
            distrat = self.speed / loc.distance_to(t)
            x = (1 / (math.sqrt(2))) * distrat * (t.longitude - loc.longitude)
            y = (1 / (math.sqrt(2))) * distrat * (t.latitude - loc.latitude)
            self.telemetry.set_location(Point(
                longitude = loc.longitude + x,
                latitude = loc.latitude + y,
                altitude = loc.altitude
            ))
            yield from asyncio.sleep(1)
