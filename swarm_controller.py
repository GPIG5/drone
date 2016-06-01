import random
import time
from enum import Enum

import math

from layer import *
from geopy.distance import great_circle


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
        self.radio_radius = config.getint('radio_radius')
        self.drone_timeout = config.getint('drone_timeout')
        self.cohesion_degree = config.getint('cohesion_degree')/100
        self.critical_avoidance_range = config.getint('critical_avoidance_range')

    def execute_layer(self, current_output):

        # print("SWARM STATE: " + str(self.state))

        if self.state == State.normal:
            # 1. Check if avoidance needed
            if self.avoidance_needed():
                return self.perform_avoidance(current_output)
            # 2. Check if coherence needed
            elif self.coherence_needed():
                return self.perform_coherence(current_output)
            # 3. Continue to searching layer
            else:
                return self.perform_normal(current_output)

        elif self.state == State.coherence:
            if self.avoidance_needed():
                return self.perform_avoidance(current_output)
            elif self.coherence_complete():
                # If coherence complete return to normal; otherwise continue with coherence
                self.aggregation_timer = time.time()
                return self.perform_normal(current_output)
            else:
                return self.perform_coherence(current_output)

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

    def coherence_needed(self):
        # The requirements for coherence are an extension of the very rudimentary requirements specified in the omega
        # algorithm to accomodate the more complex function of the swarm.
        # The idea is that if the aggregation timer runs out, we check whether the center
        # of mass would be within radio range if another aggregation timer ran out

        # return time.time() - self.aggregation_timer > self.aggregation_timeout
        if time.time() - self.aggregation_timer > self.aggregation_timeout:
            current_position = self.telemetry.get_location()
            position_of_closest = self.data_store.get_position_of_drone_closest_to(current_position,
                                                                                   timeout=self.drone_timeout)
            # center_of_mass = self.compute_neighbour_mass_center()
            if position_of_closest is not None:
                distance_to_closest = position_of_closest.distance_to(current_position)
                if distance_to_closest < self.radio_radius*0.5:
                    self.aggregation_timer = time.time()
                else:
                    return True
            else:
                return True
        else:
            return False

    def perform_coherence(self, current_output):
        if self.state != State.coherence:
            print("Coherence initiated")
            self.state = State.coherence

        if self.coherence_needed():
            current_position = self.telemetry.get_location()
            center_of_mass = self.compute_neighbour_mass_center()

            if center_of_mass is not None:
                # We move only partially towards the center of mass
                self.target = Point(
                    latitude=current_position.latitude +
                             (center_of_mass.latitude - current_position.latitude) * self.cohesion_degree,
                    longitude=current_position.longitude +
                              (center_of_mass.longitude - current_position.longitude) * self.cohesion_degree,
                    altitude=current_position.altitude +
                             (center_of_mass.altitude - current_position.altitude) * self.cohesion_degree)
            else:
                # If no neighbours in range, move towards the initial position
                print("FRIENDS LOST")
                initial_position = self.telemetry.get_initial_location()
                bearing_to_initial = current_position.bearing_to_point(initial_position)

                towards_home = current_position.point_at_vector(self.radio_radius/2, bearing_to_initial)

                if towards_home.distance_to(initial_position) > current_position.distance_to(initial_position):
                    self.target = initial_position
                else:
                    self.target = towards_home

            # print("COHERENCE INITIATED TOWARDS: " + str(self.target) +
                  # "CURRENT POSITION: " + str(current_position) +
                  # "DISTANCE: " + str(self.target.distance_to(current_position)))

        current_output.move = self.target
        if hasattr(current_output.move, 'simple_string'):
            current_output.move_info = "COHERENCE MOVE: " + current_output.move.simple_string()
        else:
            current_output.move_info = "COHERENCE MOVE"
        return current_output

    def compute_neighbour_mass_center(self):
        current_position = self.telemetry.get_location()
        neighbours_in_range = self.data_store.drones_in_range_of(current_position, self.radio_radius,
                                                                 timeout=self.drone_timeout)

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

    def coherence_complete(self):
        return self.telemetry.get_location().distance_to(self.target) < self.target_radius

    def perform_normal(self, current_output):
        if self.state != State.normal:
            self.state = State.normal
        return Layer.execute_layer(self, current_output)
