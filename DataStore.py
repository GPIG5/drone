from enum import IntEnum

def startup():
	pass

class SquareState(IntEnum):
	searched = -1
	notSearched = -2
	shouldNotSearch = -3

# gridState[x][y] - status of the (x,y) sector

class GridState:
	def __init__(self, x0, y0, xLength, yLength, squareWidth, squareHeight):
		self.x0 = x0;
		self.y0 = y0;
		self.xLenght = xLenght;		
		self.yLenght = yLenght;		
		self.squareWidth = squareWidth;		
		self.squareHeight = squareHeight;		
		self.grid = [0 for i in range(xLength)]
		for i in range(xLength):
			self.grid[i] = [SquareState.notSearched for i in range(yLength)]
			

#Neighbour positions

