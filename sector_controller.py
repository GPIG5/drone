import math

from datastore import SquareState
from enum import Enum
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
    def __init__(self, next, grid_state, telemetry, detection_radus, target_radius):
        Layer.__init__(self, next)
        self.target = None  # The target of a move
        self.target_sector_x = None
        self.target_sector_y = None
        self.grid_state = grid_state
        self.telemetry = telemetry
        self.state = State.moving
        self.detection_radius = detection_radus
        self.target_radius = target_radius
        self.searching_state = None

    def execute_layer(self, current_output):
        if self.state == State.moving:
            if self.within_target():
                if self.target_unclaimed():
                    # We claim the sector and start searching it
                    action = self.perform_search()
                    # TODO sector claim
                    return action
                else:
                    # Otherwise we calculate new target
                    self.calculate_target()
            return self.move_to_target()

        elif self.state == State.searching:
            if self.search_complete():
                # TODO broadcast completion?
                self.state = State.moving
                self.calculate_target()
                return self.move_to_target()
            else:
                return self.perform_search()

        else:
            raise UnspecifiedState(self.state)

    def target_unclaimed(self):
        return self.grid_state.grid[self.target_sector_x, self.target_sector_y] == SquareState.notSearched

    def within_target(self):
        return self.grid_state.position_within_sector(self.target_sector_x,
                                                      self.target_sector_y,
                                                      self.telemetry.get_location())

    def perform_search(self):

        if self.state != State.searching:
            # Start at top-left and scan through until the bottom right is within range
            current_position = self.telemetry.get_location()
            target_sector = self.target_sector  # TODO
            top_left = None  # TODO calculation from target sector
            detection_radius = self.detection_radius
            target_long = top_left.longitude - detection_radius
            self.target = Point(target_long, top_left.latitude, current_position.altitude)  # TODO is this correct?
            self.searching_state = SearchState.initial

        # If you are close enough to target calculate next target/do not move if complete
        if self.telemetry.get_location.distance_to(self.target) < self.target_radius:
            current_position = self.telemetry.get_location()
            target_sector = self.target_sector
            bottom_left = None  # TODO obtain from grid state
            bottom_right = None  # TODO obtain from grid state

            old_target = self.target

            if self.searching_state == SearchState.initial:
                self.searching_state = SearchState.moving_right
                self.target = Point(old_target.longitude, bottom_right.latitude, old_target.altitude)
                pass
            elif self.searching_state == SearchState.moving_right & self.searching_state == SearchState.moving_left:
                self.searching_state = SearchState.moving_down
                self.target = Point(
                    longitude=old_target.longitude-2*self.detection_radius,
                    latitude=old_target.latitude,
                    altitude=old_target.altitude
                )
            elif self.searching_state == SearchState.moving_down:
                if old_target.latitude == bottom_left.latitude:
                    self.searching_state = SearchState.moving_right
                    self.target = Point(
                        longitude=old_target.longitude,
                        latitude=bottom_right.latitude,
                        altitude=old_target.altitude
                    )
                else:
                    self.searching_state = SearchState.moving_left
                    self.target = Point(
                        longitude=old_target.longitude,
                        latitude=bottom_left.latitude,
                        altitude=old_target.altitude
                    )
        return Action(self.target)

    def calculate_target(self):
        pass

    def move_to_target(self):
        pass

    def search_complete(self):

        # The way we measure whether search is complete is by calculating how many trips are made
        # A "trip" is a single traversal of the sector from left to right or from right to left
        # If the number of trips required for a sector to be covered is even, then the search will
        # be complete when the bottom-left corner is in range; otherwise we look for bottom-right
        sector_height = 0  # TODO
        trip_count_float = sector_height / (self.detection_radius*2)
        trip_count = int(trip_count_float) + 1 if trip_count_float - int(trip_count_float) > 0 else 0

        current_location = self.telemetry.get_location()

        if trip_count % 2 == 0:
            # If the number of trips is even, then we are looking for bottom-left corner in range
            bottom_left = None  # TODO
            return current_location.distance_to(bottom_left) < self.detection_radius
        else:
            # otherwise we are looking for bottom-right
            return current_location.distance_to(bottom_right) < self.detection_radius
