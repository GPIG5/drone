import geopy
import geopy.distance

class Point:
    def __init__(self, *args, **kwargs):
        self.p = geopy.point.Point(*args, **kwargs)
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self.p.longitude = d["longitude"]
        self.p.latitude = d["latitude"]
        self.p.altitude = d["altitude"]
        return self
    @property
    def latitude(self):
        return self.p.latitude
    @property
    def longitude(self):
        return self.p.latitude
    @property
    def altitude(self):
        return self.p.latitude
    def to_json(self):
        return {
            "longitude": self.p.longitude,
            "latitude": self.p.latitude,
            "altitude": self.p.altitude
        }
    def distance_to(self, p2):
        return geopy.distance.great_circle(self.p, p2.p).meters
