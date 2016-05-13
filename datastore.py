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
            print("got message from" + d.uuid)

class SquareState(IntEnum):
    searched = -1
    notSearched = -2
    shouldNotSearch = -3


# gridState.grid[x][y] - status of the (x,y) sector
class GridState:
    def __init__(self, x0, y0, x_length, y_length, square_width, square_height):
        self.x0 = x0
        self.y0 = y0
        self.x_length = x_length
        self.y_length = y_length
        self.square_width = square_width
        self.square_height = square_height
        self.grid = [0 for i in range(x_length)]
        for i in range(x_length):
            self.grid[i] = [SquareState.notSearched for i in range(y_length)]

    # Checks whether the given position is within the sector
    def position_within_sector(self, x_of_sector, y_of_sector, position):
        leftmost_x = x_of_sector
        rightmost_x = x_of_sector + self.square_width
        bottom_y = y_of_sector
        top_y = y_of_sector + self.square_height
        return position.x > leftmost_x & position.x < rightmost_x & position.y < top_y & position.y > bottom_y


class Neighbours:
    def __init__(self, number_of_neighbours):
        self.neighbours = [None for i in range(number_of_neighbours)]

    def update_neighbour(self, index, position):
        if self.neighbours[index] is not None:
            self.neighbours[index].update_position(position)
        else:
            self.neighbours[index] = NeighbourState(position)

    # Finds the closest neighbour to the defined position
    def closest_to(self, position):
        # Find distances; fill -1 if no neighbour state defined for the given neighbour
        distances = [position.distance_to(self.neighbours[i].position) if self.neighbours[i] is not None else -1
                     for i in range(len(self.neighbours))]
        # Eliminate the -1s arising from undefined neighbour states
        valid_distances = [distances[i] if distances[i] != -1 else max(distances) for i in range(len(self.neighbours))]
        return distances.index(min(valid_distances))


# Neighbour positions
class NeighbourState:
    def __init__(self, position):
        self.position = position

    def update_position(self, position):
        self.position = position


class Position:
    def __init__(self, x_pos, y_pos, z_pos):
        self.x = x_pos
        self.y = y_pos
        self.z = z_pos

    def distance_to(self, position):
        return math.sqrt(math.pow(self.x - position.x, 2) +
                         math.pow(self.y - position.y, 2) +
                         math.pow(self.z - position.z, 2))

