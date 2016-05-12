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

class Message:
    def __init__(self, uuid, t):
        self.uuid = uuid
        self.type = t
    def to_json(self):
        return {"uuid":self.uuid,"type":self.type,"data":{}}
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self.uuid = d["uuid"]
        self.type = d["type"]
        return self

class MeshMessage(Message):
    def __init__(self, uuid, origin):
        self.origin = origin
        Message.__init__(self, uuid, "mesh")
    def to_json(self):
        d = Message.to_json(self)
        d["data"]["origin"] = self.origin
        return d
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = Message.from_json(d, self)
        self.origin = d["data"]["origin"]
        return self

class DirectMessage(Message):
    def __init__(self, uuid):
        Message.__init__(self, uuid, "direct")
    def to_json(self):
        return Message.to_json(self)
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = Message.from_json(d, self)
        return self

class StatusDirect(DirectMessage):
    def __init__(self, uuid, location, battery):
        DirectMessage.__init__(self, uuid)
        self.location = location
        self.battery = battery
    def to_json(self):
        d = DirectMessage.to_json(self)
        d["data"]["location"] = self.location.to_json()
        d["data"]["battery"] = self.battery
        d["data"]["datatype"] = "status"
        return d
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = DirectMessage.from_json(d, self)
        self.location = Point.from_json(d["data"]["location"])
        self.battery = d["data"]["battery"]
        return self

class PinorDirect(DirectMessage):
    def __init__(self, uuid, pinor):
        DirectMessage.__init__(self, uuid)
        self.pinor = pinor
    def to_json(self):
        d = DirectMessage.to_json(self)
        d["data"]["pinor"] = [x.to_json() for x in self.pinor]
        d["data"]["datatype"] = "pinor"
        return d
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = DirectMessage.from_json(d, self)
        self.pinor = [Point.from_json(x) for x in d["data"]["pinor"]]
        return self

class StatusMesh(MeshMessage):
    def __init__(self, uuid, origin, location, battery):
        MeshMessage.__init__(self, uuid, origin)
        self.location = location
        self.battery = battery
    def to_json(self):
        d = MeshMessage.to_json(self)
        d["data"]["location"] = self.location.to_json()
        d["data"]["battery"] = self.battery
        d["data"]["datatype"] = "status"
        return d
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = MeshMessage.from_json(d, self)
        self.location = Point.from_json(d["data"]["location"])
        self.battery = d["data"]["battery"]
        return self

class PinorMesh(MeshMessage):
    def __init__(self, uuid, origin, pinor):
        MeshMessage.__init__(self, uuid, origin)
        self.pinor = pinor
    def to_json(self):
        d = MeshMessage.to_json(self)
        d["data"]["pinor"] = [x.to_json() for x in self.pinor]
        d["data"]["datatype"] = "pinor"
        return d
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = MeshMessage.from_json(d, self)
        self.pinor = [Point.from_json(x) for x in d["data"]["pinor"]]
        return self
