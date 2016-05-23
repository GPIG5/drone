#!/usr/bin/env python3

import asyncio
import configparser
from enum import Enum
import uuid
import sys
from ast import literal_eval as make_tuple

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
        self.navigator = Navigator(self.config, self.datastore, self.telemetry, self.messagedispatcher)
        self.c2_reactor = self.navigator.c2_reactor
        self.mesh_controller = MeshController(self.config['DEFAULT'], self.messagedispatcher, self.communicator)
        self.engine = Engine(self.config['engine'], self.telemetry, self.navigator)

    def getUUID(self):
        return str(self.uuid)

    def getConfig(self, key = None):
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
    return(
        yield from asyncio.gather(
            *[Drone(config).run() for config in configs]
        )
    )

def multi_main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    num_drones = int(config["main"]["num_drones"])
    config = None
    configs = []
    for i in range(0, num_drones):
        config = configparser.ConfigParser()
        config.read('config.ini')
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

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(drone(config))
    loop.close()

if __name__ == "__main__":
    # execute only if run as a script
    if len(sys.argv) > 1 and sys.argv[1] == "multi":
        multi_main()
    else:
        main()
