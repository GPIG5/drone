import random
import time
from enum import Enum

import math

from layer import *
from geopy.distance import great_circle


class State(Enum):
    normal = 1
    avoidance = 2


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
        self.radio_radius = config.getint('radio_radius')
        self.drone_timeout = config.getint('drone_timeout')
        self.critical_avoidance_range = config.getint('critical_avoidance_range')

    def execute_layer(self, current_output):

        # print("SWARM STATE: " + str(self.state))

        if self.state == State.normal:
            # 1. Check if avoidance needed
            if self.avoidance_needed():
                return self.perform_avoidance(current_output)
            else:
                return self.perform_normal(current_output)
        elif self.state == State.avoidance:
            # If avoidance complete return to normal; otherwise continue with avoidance
            if self.avoidance_complete():
                # print("AVOIDANCE COMPLETE")
                self.aggregation_timer = time.time()
                return self.perform_normal(current_output)
            else:
                return self.perform_avoidance(current_output)

    # Checks whether an avoidance move is necessary in the current state
    def avoidance_needed(self):
        current_position = self.telemetry.get_location()
        position_of_closest = self.data_store.get_position_of_drone_closest_to(current_position,
                                                                               timeout=self.drone_timeout)

        if position_of_closest is not None:
            # print("Distance to closest: " + str(current_position.distance_to(position_of_closest)))
            return current_position.altitude == position_of_closest.altitude and \
                   current_position.distance_to(position_of_closest) < self.avoidance_radius
        else:
            return False

    # Returns an action that needs to be taken for avoidance
    def perform_avoidance(self, current_output):

        if self.state != State.avoidance:
            print("AVOIDANCE INITIATED")

            # If avoidance was just initiated, we need to calculate which way to avoid to
            self.state = State.avoidance

            current_position = self.telemetry.get_location()
            position_of_closest = self.data_store.get_position_of_drone_closest_to(current_position,
                                                                                   timeout=self.drone_timeout)

            avoidance_latitude = current_position.latitude - (position_of_closest.latitude - current_position.latitude)
            avoidance_longitude = current_position.longitude - (
            position_of_closest.longitude - current_position.longitude)
            avoidance_altitude = current_position.altitude

            self.target = Point(
                latitude=avoidance_latitude,
                longitude=avoidance_longitude,
                altitude=avoidance_altitude)

            distance_to_avoidance_target = self.target.distance_to(current_position)

            # If the avoidance target is too close we instead move to a random direction
            if distance_to_avoidance_target < 5:
                # print('CRITICAL AVOIDANCE DETECTED')
                self.target = great_circle(meters=self.critical_avoidance_range).destination(current_position, random.uniform(0,360))

            # print("AVOIDANCE TARGET: " + str(self.target) +
            #       "CURRENT POSITION: " + str(current_position) +
            #       "DISTANCE: " + str(distance_to_avoidance_target))

        self.aggregation_timer = time.time()
        current_output.move = self.target
        if hasattr(current_output.move, 'simple_string'):
            current_output.move_info = "AVOIDANCE MOVE: " + current_output.move.simple_string()
        else:
            current_output.move_info = "AVOIDANCE MOVE"
        return current_output

    def avoidance_complete(self):
        return self.telemetry.get_location().distance_to(self.target) < self.target_radius

    def perform_normal(self, current_output):
        if self.state != State.normal:
            self.state = State.normal
        return Layer.execute_layer(self, current_output)
