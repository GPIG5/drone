import asyncio
import itertools
from enum import Enum
from point import Point


class Drone:
    def __init__(self, uuid, battery, location):
        self.uuid = uuid
        self.battery = battery
        self.location = location



class Datastore:
    def __init__(self, messagedispatcher, detection_radius):
        self.messagedispatcher = messagedispatcher
        self.drone_state = {}
        self.detection_radius = float(detection_radius)
        self.grid_state = None

    def get_drone_state(self, uuid):
        if uuid in self.drone_state:
            return self.drone_state[uuid]
        else:
            raise "no drone with that uuid"

    def all_drones(self):
        return self.drone_state

    def get_position_of_drone_closest_to(self, position):
        closest = None
        for i in range(len(self.drone_state)):
            distance = position.distance_to(self.drone_state[i].location)
            if closest is None | closest > distance:
                closest = self.drone_state[i].location
        return closest

    def drones_in_range_of(self, position, range):
        locations_in_range = []
        for i in range(len(self.drone_state)):
            distance = position.distance_to(self.drone_state[i].location)
            if distance < range:
                locations_in_range.append(self.drone_state[i].location)
        return locations_in_range

    def get_grid_state(self):
        return self.grid_state

    def set_search_space(self, space):
        self.grid_state = GridState(space, self.detection_radius)

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


# class SectorIndex:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#
#     def __eq__(self, other):
#         if isinstance(other, self.__class__):
#             return self.x == other.x and self.y == other.y
#         return False
#
#     def __ne__(self, other):
#         return not self.__eq__(other)
#
#     def __hash__(self):
#         return self.x * self.y


class GridState:
    def __init__(self, space, detection_radius):
        bottom_left = space.bottom_left
        top_right = space.top_right
        self.origin = bottom_left

        map_width = top_right.latitude - bottom_left.latitude
        map_height = top_right.longitude - bottom_left.longitude

        pre_sector_height = 5 * detection_radius
        pre_sector_width = 5 * detection_radius

        self.y_count = int(map_height / pre_sector_height) + 1
        self.x_count = int(map_width / pre_sector_width) + 1

        self.sector_height = map_height / self.y_count
        self.sector_width = map_width / self.x_count

        self.sector_state = {(i, j): (SectorState.notSearched, 0)
                             for i, j in itertools.product(range(self.x_count), range(self.y_count))}

    # Checks whether the given position is within the sector
    def position_within_sector(self, sector_index, position):
        bottom_left = self.get_sector_origin(sector_index)
        top_right = Point(bottom_left.longitude + self.sector_height,
                          bottom_left.latitude + self.sector_width,
                          self.origin.altitude)

        return position.latitude > bottom_left.latitude & \
                                   position.latitude < top_right.latitude & \
                                                       position.longitude > bottom_left.longitude & \
                                                                            position.longitude < top_right.longitude

    def state_for(self, sector_index):
        return self.sector_state[sector_index][0]

    def drone_of(self, sector_index):
        return self.sector_state[sector_index][1]

    # returns: bottm-left, bottom-right, top-left, top-right as a list
    def get_sector_corners(self, sector_index):
        bottom_left = self.get_sector_origin(sector_index)
        bottom_right = Point(bottom_left.longitude, bottom_left.latitude + self.sector_width, bottom_left.altitude)
        top_left = Point(bottom_left.longitude + self.sector_height, bottom_left.latitude, bottom_left.altitude)
        top_right = Point(bottom_left.longitude + self.sector_height, bottom_left.latitude + self.sector_width,
                          bottom_left.altitude)
        return [bottom_left, bottom_right, top_left, top_right]

    def get_sector_origin(self, sector_index):
        latitude = self.origin.latitude + sector_index.latitude * self.sector_width
        longitude = self.origin.longitude + sector_index.longitude * self.sector_height
        return Point(longitude, latitude, self.origin.altitude)

    def get_closest_unclaimed(self, position):
        min_distance = None
        for i, j in itertools.product(range(self.x_count), range(self.y_count)):
            if self.state_for((i, j)) == SectorState.notSearched:
                distance = self.get_distance_to((i, j), position)
                if min_distance is None | min_distance[1] > distance:
                    min_distance = ((i, j), distance)
        return min_distance[0]

    def get_distance_to(self, sector_index, position):
        corners = self.get_sector_corners(sector_index)
        return min([position.distance_to(corners[i]) for i in range(4)])

# class Neighbours:
#     def __init__(self, number_of_neighbours):
#         self.neighbours = [None for i in range(number_of_neighbours)]
#
#     def update_neighbour(self, index, position):
#         if self.neighbours[index] is not None:
#             self.neighbours[index].update_position(position)
#         else:
#             self.neighbours[index] = NeighbourState(position)
#
#     # Finds the closest neighbour to the defined position
#     def closest_to(self, position):
#         # Find distances; fill -1 if no neighbour state defined for the given neighbour
#         distances = [position.distance_to(self.neighbours[i].position) if self.neighbours[i] is not None else -1
#                      for i in range(len(self.neighbours))]
#         # Eliminate the -1s arising from undefined neighbour states
#         valid_distances = [distances[i] if distances[i] != -1 else max(distances) for i in range(len(self.neighbours))]
#         return distances.index(min(valid_distances))
#
#
# # Neighbour positions
# class NeighbourState:
#     def __init__(self, position):
#         self.position = position
#
#     def update_position(self, position):
#         self.position = position
