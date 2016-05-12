
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self.x = d["x"]
        self.y = d["y"]
        return self
    def to_json(self):
        return {"x": self.x, "y": self.y}
