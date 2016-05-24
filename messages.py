from point import Point, Space
import time

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
        self.timestamp = time.time()
        Message.__init__(self, uuid, "mesh")
    def to_json(self):
        d = Message.to_json(self)
        d["data"]["origin"] = self.origin
        d["data"]["timestamp"] = self.timestamp
        return d
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = Message.from_json(d, self)
        self.origin = d["data"]["origin"]
        self.timestamp = d["data"]["timestamp"]
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
        DirectMessage.__init__(self, uuid, img = '')
        self.pinor = pinor
        self.img = img
    def to_json(self):
        d = DirectMessage.to_json(self)
        d["data"]["pinor"] = [x.to_json() for x in self.pinor]
        d["data"]["datatype"] = "pinor"
        d["data"]["img"] = self.img
        return d
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = DirectMessage.from_json(d, self)
        self.pinor = [Point.from_json(x) for x in d["data"]["pinor"]]
        self.img = d["data"]["img"]
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

class ReturnMesh(MeshMessage):
    def __init__(self, uuid, origin):
        MeshMessage.__init__(self, uuid, origin)
    def to_json(self):
        d = MeshMessage.to_json(self)
        d["data"]["datatype"] = "return"
        return d
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = MeshMessage.from_json(d, self)
        return self

class DeployMesh(MeshMessage):
    def __init__(self, uuid, origin, space):
        MeshMessage.__init__(self, uuid, origin)
        self.space = space
    def to_json(self):
        d = MeshMessage.to_json(self)
        d["data"]["space"] = self.space.to_json()
        d["data"]["datatype"] = "deploy"
        return d
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = MeshMessage.from_json(d, self)
        self.space = Space.from_json(d["data"]["space"])
        return self

class UploadDirect(DirectMessage):
    def __init__(self, uuid, images):
        DirectMessage.__init__(self, uuid)
        self.images = images
    def to_json(self):
        d = DirectMessage.to_json(self)
        d["data"]["images"] = self.images
        d["data"]["datatype"] = "upload"
        return d
    @classmethod
    def from_json(cls, d, self=None):
        if self == None:
            self = cls.__new__(cls)
        self = DirectMessage.from_json(d, self)
        self.images = d["data"]["images"]
        return self

class ClaimMesh(MeshMessage):
    def __init__(self, uuid, origin, sector_index, space):
        MeshMessage.__init__(self, uuid, origin)
        self.sector_index = sector_index
        self.space = space
    def to_json(self):
        d = MeshMessage.to_json(self)
        d['data']['sector'] = list(self.sector_index)
        d['data']['space'] = self.space.to_json()
        d['data']['datatype'] = "claim"
        return d
    @classmethod
    def from_json(cls, d, self=None):
        if self is None:
            self = cls.__new__(cls)
        self = MeshMessage.from_json(d, self)
        self.sector_index = tuple(d['data']['sector'])
        self.space = Space.from_json(d["data"]["space"])
        return self

class CompleteMesh(ClaimMesh):
    def to_json(self):
        d = ClaimMesh.to_json(self)
        d['data']['datatype'] = "complete"
        return d
