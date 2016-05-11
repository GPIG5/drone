
class Point:
<<<<<<< HEAD
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
		self = Message.from_json(data, self)
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
		self = Message.from_json(data, self)
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
		self = DirectMessage.from_json(data, self)
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
		self = DirectMessage.from_json(data, self)
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
		self = MeshMessage.from_json(data, self)
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
		self = MeshMessage.from_json(data, self)
		self.pinor = [Point.from_json(x) for x in d["data"]["pinor"]]
		return self
=======
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
>>>>>>> 2435bb262c8c67325c59103b1c55d14a0d0f8e4a
