#!/usr/bin/env python3

import asyncio
import configparser
import os
import random
from enum import Enum
import uuid
import sys
from point import Point
from ast import literal_eval as make_tuple

import sys

import io

from communicator import Communicator
from datastore import Datastore
from detection import Detection
from messagedispatcher import Messagedispatcher
from navigator import Navigator
from telemetry import Telemetry
from mesh_controller import MeshController
from engine import Engine


class Drone:
    def __init__(self, config):
        self.uuid = uuid.uuid4()
        self.config = config
        config.set('DEFAULT', 'uuid', str(self.uuid))

        self.communicator = Communicator(self.config["communicator"])
        self.messagedispatcher = Messagedispatcher(self.communicator)
        self.telemetry = Telemetry(self.config['telemetry'], self.communicator)
        self.datastore = Datastore(self.config['swarm'], self.messagedispatcher)
        self.detection = Detection(self.config['detection'], self.communicator, self.messagedispatcher)
        self.navigator = Navigator(self.config, self.datastore, self.telemetry, self.messagedispatcher, self.communicator)
        self.c2_reactor = self.navigator.c2_reactor
        self.mesh_controller = MeshController(self.config['DEFAULT'], self.messagedispatcher, self.communicator)
        self.engine = Engine(self.config['engine'], self.telemetry, self.navigator)

    def getUUID(self):
        return str(self.uuid)

    def getConfig(self, key=None):
        if key is None:
            return self.config
        elif key in self.config:
            return self.config[key]
        else:
            raise KeyError('Key: ' + key + ' not found in configuration.')

    @asyncio.coroutine
    def startup(self):
        return

    @asyncio.coroutine
    def run(self):
        inittasks = [
            self.communicator,
            self.telemetry,
            self.detection
        ]
        print("starting init tasks")
        yield from asyncio.gather(
            *[x.initialise() for x in inittasks]
        )
        tasks = [
            self,
            self.datastore,
            self.detection,
            self.messagedispatcher,
            self.navigator,
            self.telemetry,
            self.mesh_controller,
            self.engine,
            self.c2_reactor
        ]
        print("starting main tasks")
        yield from asyncio.gather(
            *[x.startup() for x in tasks]
        )


@asyncio.coroutine
def drone(*configs):
    return (
        yield from asyncio.gather(
            *[Drone(config).run() for config in configs]
        )
    )


def main(config_file):
    config = configparser.ConfigParser()

    config.read(config_file)

    num_drones = int(config["main"]["num_drones"])

    config = None

    configs = []
    for i in range(0, num_drones):
        config = configparser.ConfigParser()
        config.read(config_file)
        loc = tuple(
            [float(x) for x in make_tuple(
                config["telemetry"]["start_location"]
            )]
        )
        nloc = (loc[0] + i * 0.001, loc[1] + i * 0.001, loc[2])
        config["telemetry"]["start_location"] = str(nloc)
        configs.append(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(drone(*configs))
    loop.close()

def multi_fork_main(config_file, num_of_drones):
    config = configparser.ConfigParser()
    config.read(config_file)
    start_location = Point(*make_tuple(config['telemetry']['start_location']))
    config_names = []

    if not os.path.exists("configs"):
        os.makedirs("configs")

    # For every drone we want to start, we output a slightly modified config
    for i in range(num_of_drones):
        # Name of the new config file
        name = "config" + str(i) + ".ini"
        config_names.append(name)

        # Vary the start location a little randomly
        loc = Point(start_location.latitude + (random.uniform(0, 2) - 1) * 0.01,
                    start_location.longitude + (random.uniform(0, 2) - 1) * 0.01,
                    start_location.altitude)
        config['telemetry']['start_location'] = str((loc.latitude, loc.longitude, loc.altitude))

        # Write the config to file
        file = io.open("configs/" + name, 'w')
        config.write(file)

    # Then fork a new thread for each config we generated
    for name in config_names:
        os.system("START drone.py config configs/" + name)


if __name__ == "__main__":
    config_file = None

    arguments = sys.argv
    if len(arguments) > 2 and "config" in arguments:
        config_file = arguments[arguments.index("config") + 1]
        print("Config with: " + config_file)
    else:
        config_file = 'config.ini'

    # execute only if run as a script
    if len(arguments) > 1 and "multi" in arguments:
        multi_fork_main(config_file, int(arguments[arguments.index("multi") + 1]))
    else:
        main(config_file)

