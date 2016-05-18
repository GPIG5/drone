import geopy
import geopy.distance

class Point(geopy.point.Point):

    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = Point(
            longitude = d["lon"],
            latitude = d["lat"],
            altitude = d["alt"]
        )
        return self

    def to_json(self):
        return {
            "lon": self.longitude,
            "lat": self.latitude,
            "alt": self.altitude
        }

    def distance_to(self, p2):
        return geopy.distance.great_circle(self, p2).meters

    def perp(self, p2):
        return Point(
            longitude = self.longitude + (self.latitude - p2.latitude),
            latitude = self.latitude + (p2.longitude - self.longitude),
            altitude = self.altitude
        )

class Space:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
    def to_json(self):
        return {
            "bottom_left": self.p1.to_json,
            "top_right": self.p2.to_json
        }
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = Space(
            p1 = d["bottom_left"],
            p2 = d["top_right"]
        )
        return self
