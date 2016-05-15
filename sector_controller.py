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

class SectorController(Layer):
    def __init__(self, next, grid_state, telemetry):
        Layer.__init__(self, next)
        self.target_sector_x = None
        self.target_sector_y = None
        self.grid_state = grid_state
        self.telemetry = telemetry
        self.state = State.moving

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
            return Action(Point(0, 0, 0), True)

    def calculate_target(self):
        pass

    def move_to_target(self):
        pass

    def search_complete(self):
        pass
