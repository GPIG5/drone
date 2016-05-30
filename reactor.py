from layer import *
import importlib
from collision_detector import CollisionDetector
from battery_life_checker import BatteryLifeChecker
from person_detector import PersonDetector
from c2_reactor import C2Reactor
from sector_controller import SectorController
from swarm_controller import SwarmController
from fault_detector import FaultDetector
from image_uploader import ImageUploader
import asyncio

id = lambda x: x

class Reactor:
    def __init__(self, config, **modules):
        _layers = [
            {
                'name': 'sector_controller',
                'dependencies': ['data_store', 'telemetry'],
                'config': 'swarm',
                'class': SectorController
            },
            {
                'name': 'swarm_controller',
                'dependencies': ['data_store', 'telemetry'],
                'config': 'swarm',
                'class': SwarmController
            },
            {
                'name': 'c2_reactor',
                'dependencies': ['data_store', 'message_dispatcher', 'telemetry'],
                'class': C2Reactor
            },
            {
                'name': 'image_uploader',
                'dependencies': ['telemetry', 'detection', 'communicator'],
                'class': ImageUploader
            },
            {
                'name': 'person_detector',
                'dependencies': [],
                'class': PersonDetector
            },
            {
                'name': 'fault_detector',
                'dependencies': ['telemetry'],
                'class': FaultDetector
            },
            {
                'name': 'battery_life_checker',
                'dependencies': ['telemetry', 'communicator', 'engine'],
                'class': BatteryLifeChecker
            },
            {
                'name': 'collision_detector',
                'dependencies': ['data_store', 'telemetry'],
                'class': CollisionDetector
            }
        ]
        self.layers = {}
        next = id
        for layer in _layers:
            args = {}
            for d in layer['dependencies']:
                args[d] = modules[d]
            args['next'] = next
            if 'config' in layer:
                args['config'] = config
            obj = layer['class'](**args)
            next = obj.execute_layer
            self.layers[layer['name']] = obj
        self.entry = next
    @asyncio.coroutine
    def startup(self):
        startups = []
        for k, layer in self.layers.items():
            try:
                startups.append(layer.startup())
            except AttributeError:
                pass
        yield from asyncio.gather(*startups)
    @asyncio.coroutine
    def initialise(self):
        inits = []
        for k, layer in self.layers.items():
            try:
                inits.append(layer.initialise())
            except AttributeError:
                pass
        yield from asyncio.gather(*inits)
    def run(self):
        return self.entry(Action())
