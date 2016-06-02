from ast import literal_eval as make_tuple
import asyncio
from enum import IntEnum
import itertools
import math
import time

from point import Point, Space


class Drone:
    def __init__(self, uuid, battery, location, last_seen):
        self.uuid = uuid
        self.battery = battery
        self.location = location
        self.last_seen = last_seen

    def __str__(self, *args, **kwargs):
        return str(self.uuid) + " b:" + str(self.battery) + " l:" + str(self.location) + " t:" + str(self.last_seen)


class Datastore:
    def __init__(self, config, messagedispatcher):
        self.uuid = config.get('uuid')
        self.messagedispatcher = messagedispatcher
        self.drone_state = {}
        self.detection_radius = config.getfloat('detection_radius')
        self.grid_state = None

    def get_drone_state(self, uuid):
        if uuid in self.drone_state:
            return self.drone_state[uuid]
        else:
            raise Exception("no drone with that uuid")

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

    def compute_neighbour_mass_center(self, current_position, radio_radius=0, timeout=0):

        if radio_radius != 0:
            neighbours_in_range = self.drones_in_range_of(current_position, radio_radius, timeout)
        else:
            if timeout != 0:
                neighbours_in_range = [drone.location for asd, drone in self.drone_state.items() if drone.last_seen > time.time() - timeout]
            else:
                neighbours_in_range = [drone.location for asd, drone in self.drone_state.items()]

        if len(neighbours_in_range) != 0:
            # We find the center of mass by averaging. Mass of all points is considered 1
            totalmass = 0
            total_latitude = 0
            total_longitude = 0
            total_altitude = 0
            for i in range(len(neighbours_in_range)):
                totalmass += 1
                total_latitude += neighbours_in_range[i].latitude
                total_longitude += neighbours_in_range[i].longitude
                total_altitude += neighbours_in_range[i].altitude

            return Point(
                latitude=total_latitude / totalmass,
                longitude=total_longitude / totalmass,
                altitude=total_altitude / totalmass)
        else:
            return None

    def get_grid_state(self):
        return self.grid_state

    def set_search_space(self, space):
        self.grid_state = GridState(space, self.detection_radius)

    def get_closest_unclaimed(self, position, timeout=0):
        min_distance = (None, None)
        for i, j in itertools.product(range(self.grid_state.x_count), range(self.grid_state.y_count)):
            sector_state = self.grid_state.state_for((i, j))
            sector_drone = self.grid_state.drone_of((i, j))
            if sector_drone is not None and sector_drone != self.uuid:
                # print("STATE OF OTHER DRONES:")
                # print(self.uuid)
                # print(str(self.drone_state))
                sector_drone = self.drone_state[sector_drone]

            if sector_state == SectorState.notSearched:
                distance = self.grid_state.get_distance_to((i, j), position)
                if min_distance[0] is None or min_distance[1] > distance:
                    min_distance = ((i, j), distance)

            # If the sector has been claimed by a drone the communications from who have ceased, then we would like to
            # search this sector as well
            elif timeout != 0 and sector_state == SectorState.being_searched and sector_drone is not None and sector_drone != self.uuid:
                if sector_drone.last_seen < time.time() - timeout:
                    distance = self.grid_state.get_distance_to((i, j), position)
                    if min_distance[0] is None or min_distance[1] > distance:
                        min_distance = ((i, j), distance)

        return min_distance[0]

    @asyncio.coroutine
    def startup(self):
        yield from asyncio.gather(self.update_status(), self.update_grid())

    @asyncio.coroutine
    def update_status(self):
        while True:
            st = yield from self.messagedispatcher.wait_for_message("mesh", "status")
            d = Drone(st.origin, st.battery, st.location, st.timestamp)
            self.drone_state[d.uuid] = d
            # print("got message from: " + d.uuid)

    @asyncio.coroutine
    def update_grid(self):
        while True:
            msg = yield from self.messagedispatcher.wait_for_message("mesh", "grid")
            if self.grid_state is not None:
                self.grid_state.update(msg.grid_state.sector_state)


class SectorState(IntEnum):
    notSearched = 0
    shouldNotSearch = 1
    being_searched = 2
    searched = 3


class GridState:
    def __init__(self, space, detection_radius):
        self.space = space
        self.detection_radius = detection_radius

        horizontal_detection_radius_multiplier = 1
        vertical_detection_radius_multiplier = 1

        print("GRID INITIALISED")
        bottom_left = space.bottom_left
        top_right = space.top_right

        top_left = Point(bottom_left)
        top_left.latitude = top_right.latitude
        bottom_right = Point(bottom_left)
        bottom_right.longitude = top_right.longitude

        self.origin = Point(bottom_left)
        self.origin.altitude = 85

        map_height = bottom_left.distance_to(top_left)
        map_width = bottom_left.distance_to(bottom_right)

        pre_sector_height = detection_radius * vertical_detection_radius_multiplier
        pre_sector_width = detection_radius * horizontal_detection_radius_multiplier

        self.y_count = int(map_height / pre_sector_height) + 1
        self.x_count = int(map_width / pre_sector_width) + 1

        self.sector_height = map_height / self.y_count
        self.sector_width = map_width / self.x_count

        self.sector_state = {(i, j): [SectorState.notSearched, None]
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

    def set_state_for(self, sector_index, state, drone_uuid):
        self.sector_state[sector_index][0] = state
        self.sector_state[sector_index][1] = drone_uuid

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

    def get_distance_to(self, sector_index, position):
        corners = self.get_sector_corners(sector_index)
        return min([position.distance_to(corners[i]) for i in range(4)])

    def get_sector_space(self, sector_index):
        corners = self.get_sector_corners(sector_index)
        return Space(corners[0], corners[3])

    def update(self, new_sector_state):
        for key, value in self.sector_state.items():
            if new_sector_state[key][0] > value[0]:
                self.sector_state[key] = new_sector_state[key]

    def to_json(self):
        dict = {
            'space': self.space.to_json(),
            'detection_radius': self.detection_radius,
            'y_count': self.y_count,
            'x_count': self.x_count,
            'origin': self.origin.to_json(),
            'sector_height': self.sector_height,
            'sector_width': self.sector_width,
            'sector_state': {str(key): value for key,value in self.sector_state.items()}
        }
        # print(str(dict))
        return dict

    @classmethod
    def from_json(cls, d, self=None):
        new_sector_state = {make_tuple(key): [SectorState(value[0]), value[1]] for key,value in d['sector_state'].items()}
        if self is None:
            self = cls.__new__(cls, Space.from_json(d['space']), d['detection_radius'])
            self.sector_state = new_sector_state
            self.origin = Point.from_json(d['origin'])
            self.detection_radius = int(d['detection_radius'])
            self.y_count = int(d['y_count'])
            self.x_count = int(d['x_count'])
            self.sector_height = int(d['sector_height'])
            self.sector_width = int(d['sector_width'])

        return self
