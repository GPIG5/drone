from enum import Enum

from datastore import SectorState
from layer import *


class State(Enum):
    moving = 1
    searching = 2


class UnspecifiedState(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "The SectorContoller ended up in an invalid state: " + repr(self.value)


class SearchState(Enum):
    initial = 0
    moving_left = 1
    moving_right = 2
    moving_down = 3


class SectorController(Layer):
    def __init__(self, next, data_store, telemetry, config):
        Layer.__init__(self, next)
        self.move_target = None  # The target of a move
        self.target_sector = None
        self.data_store = data_store
        self.telemetry = telemetry
        self.state = State.moving
        self.detection_radius = config["detection_radius"]
        self.target_radius = config["target_radius"]  # The radius within which the drone must be to be considered as "arrived"
        self.searching_state = None
        self.grid_state = None

    def execute_layer(self, current_output):
        self.grid_state = self.data_store.get_grid_state()
        if (self.grid_state == None):
            return Layer.execute_layer(self, current_output)

        if self.target_sector is None:
            self.calculate_target()

        if self.state == State.moving:
            if self.within_target():
                if self.target_unclaimed():
                    # We claim the sector and start searching it
                    action = self.perform_search()
                    action.claim_sector = self.target_sector
                    return action
                else:
                    # Otherwise we calculate new target
                    self.calculate_target()
            return self.move_to_target()

        elif self.state == State.searching:
            if self.search_complete():
                self.state = State.moving
                self.calculate_target()
                return self.move_to_target()
            else:
                return self.perform_search()

        else:
            raise UnspecifiedState(self.state)

    def target_unclaimed(self):
        return self.grid_state.state_for(self.target_sector) == SectorState.notSearched

    def within_target(self):
        return self.grid_state.position_within_sector(self.target_sector,
                                                      self.telemetry.get_location())

    def perform_search(self):

        if self.state != State.searching:
            # Start at top-left and scan through until the bottom right is within range
            current_position = self.telemetry.get_location()
            top_left = self.grid_state.get_sector_corners(self.target_sector)[2]
            detection_radius = self.detection_radius
            target_long = top_left.longitude - detection_radius
            self.move_target = Point(
                latitude = top_left.latitude,
                longitude = target_long,
                altitude = current_position.altitude)
            self.searching_state = SearchState.initial

        # If you are close enough to target calculate next target/do not move if complete
        if self.telemetry.get_location.distance_to(self.move_target) < self.target_radius:
            corners = self.grid_state.get_sector_corners(self.target_sector)
            bottom_left = corners[0]
            bottom_right = corners[1]

            old_target = self.move_target

            if self.searching_state == SearchState.initial:
                self.searching_state = SearchState.moving_right
                self.move_target = Point(
                    latitude = bottom_right.latitude,
                    longitude = old_target.longitude,
                    altitude = old_target.altitude)
                pass
            elif self.searching_state == SearchState.moving_right and self.searching_state == SearchState.moving_left:
                self.searching_state = SearchState.moving_down
                self.move_target = Point(
                    longitude=old_target.longitude - 2 * self.detection_radius,
                    latitude=old_target.latitude,
                    altitude=old_target.altitude
                )
            elif self.searching_state == SearchState.moving_down:
                if old_target.latitude == bottom_left.latitude:
                    self.searching_state = SearchState.moving_right
                    self.move_target = Point(
                        longitude=old_target.longitude,
                        latitude=bottom_right.latitude,
                        altitude=old_target.altitude
                    )
                else:
                    self.searching_state = SearchState.moving_left
                    self.move_target = Point(
                        longitude=old_target.longitude,
                        latitude=bottom_left.latitude,
                        altitude=old_target.altitude
                    )
        return Action(self.move_target)

    def calculate_target(self):
        current_position = self.telemetry.get_location()
        self.target_sector = self.grid_state.get_closest_unclaimed(current_position)
        self.move_target = self.grid_state.get_sector_corners(self.target_sector)[0]

    def move_to_target(self):
        return Action(self.move_target)

    def search_complete(self):

        # The way we measure whether search is complete is by calculating how many trips are made
        # A "trip" is a single traversal of the sector from left to right or from right to left
        # If the number of trips required for a sector to be covered is even, then the search will
        # be complete when the bottom-left corner is in range; otherwise we look for bottom-right
        sector_height = self.grid_state.sector_height
        trip_count_float = sector_height / (self.detection_radius * 2)
        trip_count = int(trip_count_float) + 1 if trip_count_float - int(trip_count_float) > 0 else 0

        current_location = self.telemetry.get_location()

        corners = self.grid_state.get_sector_corners(self.target_sector)

        if trip_count % 2 == 0:
            # If the number of trips is even, then we are looking for bottom-left corner in range
            return current_location.distance_to(corners[0]) < self.detection_radius
        else:
            # otherwise we are looking for bottom-right
            return current_location.distance_to(corners[1]) < self.detection_radius
