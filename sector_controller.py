import random
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
        self.detection_radius = config.getfloat('detection_radius')
        self.target_radius = config.getfloat('target_radius')  # The radius within which the drone must be to be considered as "arrived"
        self.searching_state = None
        self.grid_state = None
        self.trip_count = 0

    def execute_layer(self, current_output):
        self.grid_state = self.data_store.get_grid_state()
        if self.grid_state is None:
            return Layer.execute_layer(self, current_output)

        if self.target_sector is None:
            self.calculate_target()

        if self.target_sector is None:
            return current_output
        else:
            if self.state == State.moving:
                if self.within_target():
                    if self.target_unclaimed():
                        # We claim the sector and start searching it
                        print("Claiming target: " + str(self.target_sector))
                        current_output.claim_sector = self.target_sector
                        return self.perform_search(current_output)
                    else:
                        # Otherwise we calculate new target
                        self.calculate_target()

                # Else if the target got claimed while moving, calculate new target
                elif not self.target_unclaimed():
                    self.calculate_target()
                return self.move_to_target(current_output)
            elif self.state == State.searching:
                if self.search_complete():
                    print("Search complete")
                    current_output.complete_sector = self.target_sector
                    self.state = State.moving
                    self.calculate_target()
                    return self.move_to_target(current_output)
                else:
                    return self.perform_search(current_output)
            else:
                raise UnspecifiedState(self.state)

    def target_unclaimed(self):
        return self.grid_state.state_for(self.target_sector) == SectorState.notSearched

    def within_target(self):
        return self.grid_state.position_within_sector(self.target_sector,
                                                      self.telemetry.get_location())

    def perform_search(self, current_output):
        if self.state != State.searching:
            # Start at top-left and scan through until the bottom right is within range
            current_position = self.telemetry.get_location()
            top_left = self.grid_state.get_sector_corners(self.target_sector)[2]
            self.move_target = top_left.point_at_vector(self.detection_radius, 180)
            self.move_target.altitude -= random.uniform(1, 11)
            self.state = State.searching
            self.searching_state = SearchState.initial
            self.trip_count = 0

        # If you are close enough to target calculate next target/do not move if complete
        if self.telemetry.get_location().distance_to(self.move_target) < self.target_radius:
            corners = self.grid_state.get_sector_corners(self.target_sector)
            bottom_left = corners[0]
            bottom_right = corners[1]

            old_target = self.move_target

            if self.searching_state == SearchState.initial:
                self.searching_state = SearchState.moving_right
                self.move_target = old_target.point_at_vector(self.grid_state.sector_width, 90)

            elif self.searching_state == SearchState.moving_right or self.searching_state == SearchState.moving_left:
                self.old_search_state = self.searching_state
                self.trip_count += 1
                self.searching_state = SearchState.moving_down
                self.move_target = old_target.point_at_vector(self.detection_radius*2, 180)

            elif self.searching_state == SearchState.moving_down:
                if self.old_search_state == SearchState.moving_left:
                    self.searching_state = SearchState.moving_right
                    self.move_target = old_target.point_at_vector(self.grid_state.sector_width, 90)
                else:
                    self.searching_state = SearchState.moving_left
                    self.move_target = old_target.point_at_vector(self.grid_state.sector_width, 270)

        current_output.move = self.move_target
        if hasattr(current_output.move, 'simple_string'):
            current_output.move_info = "SEARCHING MOVE: " + current_output.move.simple_string()
        else:
            current_output.move_info = "SEARCHING MOVE"
        return current_output

    def calculate_target(self):
        current_position = self.telemetry.get_location()
        self.target_sector = self.data_store.get_closest_unclaimed(current_position, 10)
        if self.target_sector is not None:
            corners = self.grid_state.get_sector_corners(self.target_sector)

            self.move_target = Point(
                longitude=(corners[0].longitude + corners[3].longitude) / 2,
                latitude=(corners[0].latitude + corners[3].latitude) / 2,
                altitude=corners[0].altitude
            )
            self.move_target = corners[0]
            print('Move Target: ' + str(self.move_target))
        else:
            # If no more unclaimed targets exist, go back home
            self.move_target = self.telemetry.get_initial_location()

    def move_to_target(self, current_output):
        if self.move_target is not None:
            current_output.move = self.move_target
            if hasattr(current_output.move, 'simple_string'):
                current_output.move_info = "SECTOR MOVE: " + current_output.move.simple_string()
            else:
                current_output.move_info = "SECTOR MOVE"
        return current_output

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

        if trip_count == self.trip_count:
            if trip_count % 2 == 0:
                # If the number of trips is even, then we are looking for bottom-left corner in range
                return current_location.distance_to(corners[0]) < self.detection_radius
            else:
                # otherwise we are looking for bottom-right
                return current_location.distance_to(corners[1]) < self.detection_radius
        else:
            return False
