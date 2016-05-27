from layer import *
import importlib
from collision_detector import CollisionDetector
from battery_life_checker import BatteryLifeChecker
from person_detector import PersonDetector
from c2_reactor import C2Reactor
from sector_controller import SectorController
from swarm_controller import SwarmController

id = lambda x: x

class Reactor:
    def __init__(self, config, data_store, telemetry, message_dispatcher, communicator):
        secc = SectorController(id, data_store, telemetry, config["swarm"])
        swc = SwarmController(secc.execute_layer, config["swarm"], data_store, telemetry)
        c2 = C2Reactor(swc.execute_layer, data_store, message_dispatcher, telemetry)
        pd = PersonDetector(c2.execute_layer)
        bl = BatteryLifeChecker(pd.execute_layer, telemetry, config["DEFAULT"], communicator, int(config['engine']['speed']))
        cd = CollisionDetector(bl.execute_layer, data_store, telemetry)
        self.entry = cd.execute_layer
        self.c2_reactor = c2
    def run(self):
        return self.entry(Action())
