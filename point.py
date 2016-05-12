
class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self.x = d["x"]
        self.y = d["y"]
        self.z = d["z"]
        return self
    def to_json(self):
        return {"x": self.x, "y": self.y, "z": self.z}
