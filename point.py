import geopy
from geopy.distance import great_circle

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
        return great_circle(self, p2).meters

    def perp(self, p2):
        return Point(
            longitude = self.longitude + (self.latitude - p2.latitude),
            latitude = self.latitude + (p2.longitude - self.longitude),
            altitude = self.altitude
        )

    def point_at_vector(self, distance, bearing):
        if distance == 0:
            return Point(self)
        else:
            point = Point(great_circle(meters=distance).destination(self, bearing))
            point.altitude = self.altitude
            return point

class Space:
    def __init__(self, bottom_left, top_right):
        self.bottom_left = bottom_left
        self.top_right = top_right
    def to_json(self):
        return {
            "bottom_left": self.bottom_left.to_json(),
            "top_right": self.top_right.to_json()
        }
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = Space(
            bottom_left = Point.from_json(d["bottom_left"]),
            top_right = Point.from_json(d["top_right"])
        )
        return self

