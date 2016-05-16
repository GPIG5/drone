import time
from enum import Enum
from layer import *


class State(Enum):
    normal = 1
    coherence = 2
    avoidance = 3


class SwarmController(Layer):
    def __init__(self, next, config, data_store, telemetry):
        Layer.__init__(self, next)
        self.state = State.normal
        self.data_store = data_store
        self.telemetry = telemetry
        self.avoidance_target = None
        self.aggregation_timer = time.time()
        self.target = None

        self.avoidance_radius = config.getint('avoidance_radius')
        self.aggregation_timeout = config.getint('aggregation_timeout')
        self.target_radius = config.getint('target_radius')

    def execute_layer(self, current_output):
        if self.state == State.normal:
            # 1. Check if avoidance needed
            if self.avoidance_needed():
                return self.perform_avoidance()
            # 2. Check if coherence needed
            elif self.coherence_needed():
                return self.perform_coherence()
            # 3. Continue to searching layer
            else:
                return self.perform_normal(current_output)

        elif self.state == State.coherence:
            if self.avoidance_needed():
                return self.perform_avoidance()
            elif self.coherence_complete():
                # If coherence complete return to normal; otherwise continue with coherence
                self.aggregation_timer = time.time()
                self.perform_normal(current_output)
            else:
                return self.perform_coherence()

        elif self.state == State.avoidance:
            # If avoidance complete return to normal; otherwise continue with avoidance
            if self.avoidance_complete():
                self.aggregation_timer = time.time()
                self.perform_normal(current_output)
            else:
                return self.perform_coherence()

    # Checks whether an avoidance move is necessary in the current state
    def avoidance_needed(self):
        position_of_closest = Point(0, 0, 0)  # TODO
        current_position = self.telemetry.get_location()
        return current_position.distance_to(position_of_closest) < self.avoidance_radius

    # Returns an action that needs to be taken for avoidance
    def perform_avoidance(self):

        if self.state != State.avoidance:
            # If avoidance was just initiated, we need to calculate which way to avoid to
            self.state = State.avoidance

            position_of_closest = Point(0,0,0)  # TODO
            current_position = self.telemetry.get_location()
            avoidance_latitude = current_position.latitude + (position_of_closest.latitude - current_position.latitude)
            avoidance_longitude = current_position.longitude + (position_of_closest.longitude - current_position.longitude)
            avoidance_altitude = current_position.altitude + (position_of_closest.latitude - current_position.altitude)
            self.target = Point(avoidance_latitude, avoidance_longitude, avoidance_altitude)

        self.aggregation_timer = time.time()
        return Action(self.target)

    def avoidance_complete(self):
        return True #self.telemetry.get_location().distance_to(self.target) < self.telemetry

    def coherence_needed(self):
        return self.aggregation_timer - time.time() > self.aggregation_timeout

    def perform_coherence(self):

        if self.state != State.coherence:
            # If avoidance was just initiated, we need to calculate which way to avoid to
            self.state = State.coherence

            neighbours_in_range = [Point(0,0,0), Point(0,0,0), Point(0,0,0)]  # TODO - positions of neighbours in range

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

            self.target = Point(total_latitude / totalmass, total_y / totalmass, total_altitude / totalmass)

        return Action(self.target)

    def coherence_complete(self):
        return True#self.telemetry.get_location().distance_to(self.target) < self.telemetry

    def perform_normal(self, current_output):
        if self.state != State.normal:
            self.state = State.normal
        return self.next(current_output)
