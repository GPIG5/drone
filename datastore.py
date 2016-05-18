from enum import Enum
import asyncio

import itertools


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

    def all_drones(self):
        return self.drone_state

    @asyncio.coroutine
    def startup(self):
        while True:
            st = yield from self.messagedispatcher.wait_for_message("mesh", "status")
            d = Drone(st.origin, st.battery, st.location)
            self.drone_state[d.uuid] = d
            print("got message from" + d.uuid)


class SectorState(Enum):
    searched = 1
    notSearched = 2
    shouldNotSearch = 3
    being_searched = 4


class SectorIndex:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.x * self.y


# gridState.grid[x][y] - status of the (x,y) sector
class GridState:
    def __init__(self, bottom_left, top_right, detection_radius):
        self.origin = bottom_left

        map_width = top_right.latitude - bottom_left.latitude
        map_height = top_right.longitude - bottom_left.longitude

        pre_sector_height = 5 * detection_radius
        pre_sector_width = 5 * detection_radius

        self.y_count = int(map_height / pre_sector_height) + 1
        self.x_count = int(map_width / pre_sector_width) + 1

        self.sector_height = map_height / self.y_count
        self.sector_width = map_width / self.x_count

        self.sector_state = {SectorIndex(i, j): SectorState.notSearched
                             for i, j in itertools.product(range(self.x_count), range(self.x_count))}

        # Checks whether the given position is within the sector
        # def position_within_sector(self, sector_index, position):
        #     leftmost_latitude = sector_index.x
        #     rightmost_x = x_of_sector + self.square_width
        #     bottom_y = y_of_sector
        #     top_y = y_of_sector + self.square_height
        #     return position.x > leftmost_x & position.x < rightmost_x & position.y < top_y & position.y > bottom_y


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
