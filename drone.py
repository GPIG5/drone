
import asyncio
import configparser
from enum import Enum
import uuid

from communicator import Communicator
import datastore
import detection
import messagedispatcher
import navigator
import telemetry

class Drone:
    def __init__(self, config):
        self.uuid = uuid.uuid4()
        self.config = config

        self.comms = Communicator(self)

    def getUUID():
        return self.uuid

    def getConfig(key = None):
        if key is None:
            return self.config
        elif key in self.config:
            return self.config[key]
        else
            raise KeyError('Key: ' + key + ' not found in configuration.')

    def run():
        pass


def main():
    config = configparser.ConfigParser
    config.read('config.ini')

    drone = Drone(config)
    drone.run()

if __name__ == "__main__":
    # execute only if run as a script
    main()
