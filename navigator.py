import asyncio
import time
import configparser
from enum import Enum
import datastore


class Navigator:
	def __init__(self, messagedispatcher):
		self.messagedispatcher = messagedispatcher

	@asyncio.coroutine
	def startup(self):
		pass

class State(Enum):
    move = 1
    search = 2
    avoid = 3
    recharge = 4
    coherence = 5
    rendezvous = 6


class Navigator:
    def __init__(self, self_id, grid_state, telemetry, neighbours, engine):
        self.id = self_id
        self.state = State.move
        self.grid = grid_state
        self.telemetry = telemetry
        self.neighbours = neighbours
        self.engine = engine

    def loop(self):
        # TODO enough battery life?
        if self.state == State.move:
            self.when_move()
        elif self.state == State.search:
            self.when_search()
        elif self.state == State.avoid:
            self.when_avoid()
        elif self.state == State.recharge:
            self.when_recharge()
        elif self.state == State.coherence:
            self.when_coherence()
        elif self.state == State.rendezvous:
            self.when_rendezvous()

    def when_move(self):
        pass

    def when_search(self):
        pass

    def when_recharge(self):
        pass

    def when_cohere(self):
        pass

    def when_avoid(self):
        pass

    def when_coherence(self):
        pass

    def when_rendezvous(self):
        pass


# Omega-algorithm based navigator
# "Avoidance" refers to 2 circumstances (and causes different reactions):
#   - When you get too close to another drone:  turn away from the direction of this droid and fly for a bit then
#       recalculate
#   - When you arrive to a sector and it is occuppied: recalculate target
#
#
class OmegaNavigator(Navigator):
    def __init__(self, self_id, grid_state, telemetry, neighbours, engine):
        super().__init__(self_id, grid_state, telemetry, neighbours, engine)
        self.avoidance_target = None
        self.aggregation_timer = time.time()
        # TODO initialise target
        # target = the sector as identified by the grid coordinates
        self.target = None

        config = configparser.ConfigParser()
        config.read('navigator.cfg')
        omega = config['Omega']

        self.avoidance_radius = omega['avoidance_radius']
        self.aggregation_timeout = omega['aggregation_timeout']
        self.avoid_until_range = omega['avoid_until_range']

    def when_move(self):
        # 1. Check for avoidance
        # TODO doesn't account for multiple neighbours in range
        current_position = self.telemetry.current_position()
        closest_neighbour = self.neighbours.closest_to(current_position)

        if current_position.distance_to(self.neighbours[closest_neighbour].position) < self.avoidance_radius:
            self.avoidance_target = closest_neighbour
            self.state = State.avoid
            pass

        # 2. Check if coherence move is necessary
        if self.aggregation_timer - time.time() > self.aggregation_timeout:
            self.state = State.coherence
            pass

        # 3. Check if arrived; switch to search or recalculate
        x, y = self.target[1], self.target[2]
        if self.grid.position_within_sector(x, y, current_position):
            # We have arrived!
            if self.grid.grid[x][y] == datastore.SquareState.notSearched:
                #TODO communicate the search update
                #TODO datastore update - should be thread safe
                self.grid.grid[x][y] = self.id
                self.state = State.search
                pass
            else:
                self.recalculate_target()

        # 4. If we're still trying to move, move towards target
        self.engine.moveTowards(datastore.Position(self.target[1], self.target[2], current_position.z))

    # Performs the avoidance maneuver away from the specified neighbour
    def when_avoid(self):
        pass

    def recalculate_target(self):
        pass

