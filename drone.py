#!/usr/bin/env python3

import asyncio
import configparser
from enum import Enum
import uuid

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
        self.datastore = Datastore(self.messagedispatcher)
        self.detection = Detection(self.config['detection'], self.communicator, self.messagedispatcher)
        self.navigator = Navigator(self.config, self.datastore, self.telemetry, self.messagedispatcher)
        self.mesh_controller = MeshController(self.messagedispatcher, self, self.communicator)
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

    def run(self):
        loop = asyncio.get_event_loop()
        inittasks = [
            self.communicator,
            self.telemetry,
            self.detection
        ]
        print("starting init tasks")
        loop.run_until_complete(asyncio.gather(
            *[x.initialise() for x in inittasks]
        ))
        tasks = [
            self,
            self.datastore,
            self.detection,
            self.messagedispatcher,
            self.navigator,
            self.telemetry,
            self.mesh_controller,
            self.engine
        ]
        print("starting main tasks")
        loop.run_until_complete(asyncio.gather(
            *[x.startup() for x in tasks]
        ))
        loop.close()


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    drone = Drone(config)
    drone.run()

if __name__ == "__main__":
    # execute only if run as a script
    main()
