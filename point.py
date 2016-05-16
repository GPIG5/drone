import geopy
import geopy.distance

class Point:
    def __init__(self, *args, **kwargs):
        self.p = geopy.point.Point(*args, **kwargs)
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self.p = geopy.point.Point(
            longitude = d["long"],
            latitude = d["lat"],
            altitude = d["alt"]
        )
        return self
    @property
    def latitude(self):
        return self.p.latitude
    @property
    def longitude(self):
        return self.p.longitude
    @property
    def altitude(self):
        return self.p.altitude
    def to_json(self):
        return {
            "long": self.longitude,
            "lat": self.latitude,
            "alt": self.altitude
        }
    def distance_to(self, p2):
        return geopy.distance.great_circle(self.p, p2.p).meters
    def perp(self, p2):
        return Point(
            longitude = self.longitude + (self.latitude - p2.latitude),
            latitude = self.latitude + (p2.longitude - self.longitude),
            altitude = self.altitude
        )


class Sector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
