from enum import IntEnum
import asyncio

class Drone:
	def __init__(self, uuid, battery, location):
		self.uuid = uuid
		self.battery = battery
		self.location = location

class Datastore:
	def __init__(self, messagedispatcher):
		self.messagedispatcher = messagedispatcher
		self.drone_state = {}

	def get_drone_state(self, uuid):
		if uuid in self.drone_state:
			return self.drone_state[uuid]
		else:
			raise "no drone with that uuid"

	@asyncio.coroutine
	def startup(self):
		while True:
			st = yield from self.messagedispatcher.wait_for_message("mesh", "status")
			d = Drone(st.origin, st.battery, st.location)
			self.drone_state[d.uuid] = d

class SquareState(IntEnum):
	searched = -1
	notSearched = -2
	shouldNotSearch = -3

# gridState[x][y] - status of the (x,y) sector

class GridState:
	def __init__(self, x0, y0, xLength, yLength, squareWidth, squareHeight):
		self.x0 = x0
		self.y0 = y0
		self.xLenght = xLenght
		self.yLenght = yLenght
		self.squareWidth = squareWidth
		self.squareHeight = squareHeight
		self.grid = [0 for i in range(xLength)]
		for i in range(xLength):
			self.grid[i] = [SquareState.notSearched for i in range(yLength)]


#Neighbour positions

