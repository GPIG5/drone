import asyncio
from enum import Enum
from geopy.distance import great_circle
import time
import itertools
import math
from point import Point


class Drone:
    def __init__(self, uuid, battery, location, last_seen):
        self.uuid = uuid
        self.battery = battery
        self.location = location
        self.last_seen = last_seen


class Datastore:
    def __init__(self, config, messagedispatcher):
        self.messagedispatcher = messagedispatcher
        self.drone_state = {}
        self.detection_radius = config.getfloat('detection_radius')
        self.grid_state = None

    def get_drone_state(self, uuid):
        if uuid in self.drone_state:
            return self.drone_state[uuid]
        else:
            raise "no drone with that uuid"

    def all_drones(self):
        return self.drone_state

    def get_position_of_drone_closest_to(self, position, timeout=0):
        closest = None
        closest_distance = None
        for uuid, drone in self.drone_state.items():
            distance = position.distance_to(drone.location)
            # Only consult drones that haven't timed out if timeout != 0
            if (closest is None or closest_distance > distance) \
                    and (timeout == 0 or time.time() - drone.last_seen < timeout):
                closest = drone.location
                closest_distance = distance
        return closest

    def drones_in_range_of(self, position, drone_range, timeout=0):
        locations_in_range = []
        for uuid, drone in self.drone_state.items():
            distance = position.distance_to(drone.location)
            if distance < drone_range and (timeout == 0 or time.time() - drone.last_seen < timeout):
                locations_in_range.append(drone.location)
        return locations_in_range

    def get_grid_state(self):
        return self.grid_state

    def set_search_space(self, space):
        self.grid_state = GridState(space, self.detection_radius)

    @asyncio.coroutine
    def startup(self):
        while True:
            st = yield from self.messagedispatcher.wait_for_message("mesh", "status")
            d = Drone(st.origin, st.battery, st.location, st.timestamp)
            self.drone_state[d.uuid] = d
            # print("got message from: " + d.uuid)


class SectorState(Enum):
    searched = 1
    notSearched = 2
    shouldNotSearch = 3
    being_searched = 4


class GridState:
    def __init__(self, space, detection_radius):
        detection_radius_multiplier = 15/12
        print("GRID INITIALISED")
        bottom_left = space.bottom_left
        top_right = space.top_right

        top_left = Point(bottom_left)
        top_left.latitude = top_right.latitude
        bottom_right = Point(bottom_left)
        bottom_right.longitude = top_right.longitude

        self.origin = Point(bottom_left)
        self.origin.altitude = 75

        map_height = bottom_left.distance_to(top_left)
        map_width = bottom_left.distance_to(bottom_right)

        pre_sector_height = detection_radius*detection_radius_multiplier
        pre_sector_width = detection_radius*detection_radius_multiplier

        self.y_count = int(map_height / pre_sector_height) + 1
        self.x_count = int(map_width / pre_sector_width) + 1

        self.sector_height = map_height / self.y_count
        self.sector_width = map_width / self.x_count

        self.sector_state = {(i, j): [SectorState.notSearched, 0]
                             for i, j in itertools.product(range(self.x_count), range(self.y_count))}

    # Checks whether the given position is within the sector
    def position_within_sector(self, sector_index, position):
        bottom_left = self.get_sector_origin(sector_index)
        distance = math.hypot(self.sector_width, self.sector_height)
        top_right = bottom_left.point_at_vector(distance, 45)

        return position.latitude >= bottom_left.latitude and \
               position.latitude <= top_right.latitude and \
               position.longitude >= bottom_left.longitude and \
               position.longitude <= top_right.longitude

    def set_state_for(self, sector_index, state):
        self.sector_state[sector_index][0] = state

    def state_for(self, sector_index):
        return self.sector_state[sector_index][0]

    def drone_of(self, sector_index):
        return self.sector_state[sector_index][1]

    # returns: bottom-left, bottom-right, top-left, top-right as a list
    def get_sector_corners(self, sector_index):
        bottom_left = self.get_sector_origin(sector_index)
        bottom_right = bottom_left.point_at_vector(self.sector_width, 90)
        top_left = bottom_left.point_at_vector(self.sector_height, 0)
        top_right = bottom_right.point_at_vector(self.sector_height, 0)
        # print(' bl: ' + str(bottom_left) + '\n br: ' + str(bottom_right) + '\n tl: ' + str(top_left) + '\n tr: ' + str(top_right))
        return [bottom_left, bottom_right, top_left, top_right]

    def get_sector_origin(self, sector_index):
        return self.origin.point_at_xy_distance(sector_index[0] * self.sector_width, sector_index[1] * self.sector_height)

    def get_closest_unclaimed(self, position):
        min_distance = (None, None)
        for i, j in itertools.product(range(self.x_count), range(self.y_count)):
            if self.state_for((i, j)) == SectorState.notSearched:
                distance = self.get_distance_to((i, j), position)
                if min_distance[0] is None or min_distance[1] > distance:
                    min_distance = ((i, j), distance)
        return min_distance[0]

    def get_distance_to(self, sector_index, position):
        corners = self.get_sector_corners(sector_index)
        return min([position.distance_to(corners[i]) for i in range(4)])
