import geopy
import math
from geopy.distance import great_circle
import uuid

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

    def perp(self, p2, dist, duuid):
        b = self.bearing_to_point(p2)
        h = 1.0 / float(
            int.from_bytes(
                b"\xff" * 16
            ) / int.from_bytes(
                UUID(duuid).bytes, byteorder='big'
            )
        )
        b += 180 + ((h * 180) - 90)
        return self.point_at_vector(10 - dist, b)

    def bearing_to_point(self, target_location):
        # algorithm from https://gist.github.com/jeromer/2005586

        lat1 = math.radians(self.latitude)
        lat2 = math.radians(target_location.latitude)
        diffLong = math.radians(target_location.longitude - self.longitude)

        x = math.sin(diffLong) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))

        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)
        bearing = (initial_bearing + 360) % 360
        return bearing

    def point_at_vector(self, distance, bearing):
        if distance == 0:
            return Point(self)
        else:
            point = Point(great_circle(meters=distance).destination(self, bearing))
            point.altitude = self.altitude
            return point

    def point_at_xy_distance(self, x_dist, y_dist):
        lat = great_circle(meters=y_dist).destination(self, 0).latitude if y_dist > 0 else self.latitude
        lon = great_circle(meters=x_dist).destination(self, 90).longitude if x_dist > 0 else self.longitude
        return Point(latitude = lat, longitude = lon, altitude = self.altitude)

    def simple_string(self):
        return str(self.latitude) + " " + str(self.longitude) + " " + str(self.altitude)

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
        if self is None:
            self = cls.__new__(cls)
        self = Space(
            bottom_left = Point.from_json(d["bottom_left"]),
            top_right = Point.from_json(d["top_right"])
        )
        return self

