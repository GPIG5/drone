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
import multiprocessing
import shutil

import sys

import io
import subprocess

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
        self.telemetry = Telemetry(self.config['telemetry'], self.communicator, self.config['defects'], int(self.config['engine']['travel_time']))
        self.datastore = Datastore(self.config['swarm'], self.messagedispatcher)
        self.detection = Detection(self.config['detection'], self.communicator, self.messagedispatcher, self.telemetry)
        self.navigator = Navigator(self.config, self.datastore, self.telemetry, self.messagedispatcher, self.communicator, self.detection)
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
            self.navigator.reactor.c2_reactor,
            self.navigator.reactor.battery_life_checker,
            self.navigator.reactor.pit_stop
        ]
        print("starting main tasks")
        yield from asyncio.gather(
            *[x.startup() for x in tasks]
        )

@asyncio.coroutine
def codrone(configs):
    return (
        yield from asyncio.gather(
            *[drone(config) for config in configs]
        )
    )

@asyncio.coroutine
def drone(config):
    return (
        yield from Drone(config).run()
    )

def run_coroutine(coroutine, arg):
    oldloop = asyncio.get_event_loop()
    oldloop.close()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ret = loop.run_until_complete(coroutine(arg))
    loop.close()
    return ret

def run_codrone(configs):
    return run_coroutine(codrone, configs)

def run_drone(config):
    return run_coroutine(drone, config)

def main():
    oldloop = asyncio.get_event_loop()
    oldloop.close()

    print("Bootstrapping drone configuration")
    config = configparser.ConfigParser()
    config.read("config.ini")
    num_drones = int(config["main"]["num_drones"])
    df = config['detection']['data_folder']
    if os.path.exists(df):
        print("deleting data")
        shutil.rmtree(df)
    os.mkdir(df)
    config = None

    print("Generating subconfigurations")
    configs = []
    for i in range(0, num_drones):
        config = configparser.ConfigParser()
        config.read("config.ini")
        loc = tuple(
            [float(x) for x in make_tuple(
                config["telemetry"]["start_location"]
            )]
        )
        nloc = (
            loc[0] + (i * 0.0001 * (random.uniform(0, 2) - 1)),
            loc[1] + (i * 0.0001 * (random.uniform(0, 2) - 1)),
            loc[2]
        )
        config["telemetry"]["start_location"] = str(nloc)
        configs.append(config)

    return multi_drone_hybrid(configs)

def run_processes(func, args):
    ps = []
    for a in args:
        ps.append(multiprocessing.Process(target=func, args=(a,)))
    for p in ps:
        p.start()
    for p in ps:
        p.join()
    return ps

def multi_drone_hybrid(configs):
    print("Beginning hybrid multidrone")
    try:
        cpus = multiprocessing.cpu_count()
        print("detected number of cpus as " + str(cpus))
    except NotImplementedError as e:
        cpus = 8
        print("could not detect number of cpus, assuming " + str(spus))
    current_configs = configs
    processes = []
    processes_drone_num = []
    for i in range(0, cpus):
        n = int(round(float(len(current_configs)) / float(cpus - i)))
        if (n > 0):
            processes.append(current_configs[:n])
            processes_drone_num.append(n)
            current_configs = current_configs[n:]
    print("Using hybrid configuration: " + " ".join(str(x) for x in processes_drone_num))
    return run_processes(run_codrone, processes)

if __name__ == "__main__":
    main()
