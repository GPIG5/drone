
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def to_json(self):
        return {"x": self.x, "y": self.y}

class Message:
    def __init__(self, uuid, t):
        self.uuid = uuid
        self.type = t
    def to_json(self):
        return {"uuid":self.uuid,"type":self.type,"data":{}}

class MeshMessage(Message):
    def __init__(self, uuid, origin):
        super(MeshMessage, self).__init__(uuid, "mesh")
        self.origin = origin

    def to_json(self):
        d = super(MeshMessage, self).to_json()
        d["data"]["origin"] = self.origin
        return d

class DirectMessage(Message):
    def __init__(self, uuid):
        super(DirectMessage, self).__init__(uuid, "direct")
    def to_json(self):
        return super(DirectMessage, self).to_json()

class StatusDirect(DirectMessage):
    def __init__(self, uuid, location, battery):
        super(StatusDirect, self).__init__(uuid)
        self.location = location
        self.battery = battery
    def to_json(self):
        d = super(StatusDirect, self).to_json(self)
        d["data"]["location"] = self.location.to_json()
        d["data"]["battery"] = self.battery
        d["data"]["datatype"] = "status"
        return d

class PinorDirect(DirectMessage):
    def __init__(self, uuid, pinor):
        super(PinorDirect, self).__init__(uuid)
        self.pinor = pinor
    def to_json(self):
        d = super(PinorDirect, self).to_json(self)
        d["data"]["pinor"] = [x.to_json() for x in self.pinor]
        d["data"]["datatype"] = "pinor"
        return d

class StatusMesh(MeshMessage):
    def __init__(self, uuid, origin, location, battery):
        super(StatusMesh, self).__init__(uuid, origin)
        self.location = location
        self.battery = battery
    def to_json(self):
        d = super(StatusMesh, self).to_json(self)
        d["data"]["location"] = self.location.to_json()
        d["data"]["battery"] = self.battery
        d["data"]["datatype"] = "status"
        return d

class PinorMesh(MeshMessage):
    def __init__(self, uuid, origin, pinor):
        super(PinorMesh, self).__init__(uuid, origin)
        self.pinor = pinor
    def to_json(self):
        d = super(PinorMesh, self).to_json(self)
        d["data"]["pinor"] = [x.to_json() for x in self.pinor]
        d["data"]["datatype"] = "pinor"
        return d
