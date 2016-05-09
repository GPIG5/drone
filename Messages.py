
class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y
	def to_json(self):
		return {"x": self.x, "y": self.y}

class Message:
	def __init__(self, uuid, t, data):
		self.uuid = uuid
		self.type = t
		self.data = data
	def to_json(self):
		return {"uuid":self.uuid,"type":self.type,"data":self.data.to_json()}

class MeshMessage(Message):
	def __init__(self, uuid, data):
		Message.__init(uuid, "mesh", data)
	def to_json(self):
		return Message.to_json()

class DirectMessage(Message):
	def __init__(self, uuid, data):
		Message.__init(uuid, "direct", data)
	def to_json(self):
		return Message.to_json()
