
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
		self.origin = origin
		Message.__init(uuid, "mesh")
	def to_json(self):
		d = Message.to_json(self)
		d["data"]["origin"] = self.origin
		return d

class DirectMessage(Message):
	def __init__(self, uuid):
		Message.__init(uuid, "direct")
	def to_json(self):
		return Message.to_json(self)

class StatusDirect(DirectMessage):
	def __init__(self, location, battery):
		self.location = location
		self.battery = battery
	def to_json(self):
		d = DirectMessage.to_json(self)
		d["data"]["location"] = self.location.to_json()
		d["data"]["battery"] = self.battery
		d["data"]["datatype"] = "status"
		return d

class PinorDirect(DirectMessage):
	def __init__(self, pinor):
		self.pinor = pinor
	def to_json(self):
		d = DirectMessage.to_json(self)
		d["data"]["pinor"] = [x.to_json() for x in self.pinor]
		d["data"]["datatype"] = "pinor"
		return d

class StatusMesh(MeshMessage):
	def __init__(self, location, battery):
		self.location = location
		self.battery = battery
	def to_json(self):
		d = MeshMessage.to_json(self)
		d["data"]["location"] = self.location.to_json()
		d["data"]["battery"] = self.battery
		d["data"]["datatype"] = "status"
		return d

class PinorMesh(MeshMessage):
	def __init__(self, pinor):
		self.pinor = pinor
	def to_json(self):
		d = MeshMessage.to_json(self)
		d["data"]["pinor"] = [x.to_json() for x in self.pinor]
		d["data"]["datatype"] = "pinor"
		return d
