from layer import *
import importlib
from collision_detector import CollisionDetector
from battery_life_checker import BatteryLifeChecker
from person_detector import PersonDetector
from c2_reactor import C2Reactor
from sector_controller import SectorController
from swarm_controller import SwarmController
from pit_stop import PitStop
import time

id = lambda x: x

class Reactor:
    def __init__(self, config, data_store, telemetry, message_dispatcher, communicator, detection):
        secc = SectorController(id, data_store, telemetry, config["swarm"])
        swc = SwarmController(secc.execute_layer, config["swarm"], data_store, telemetry)
        ps = PitStop(swc.execute_layer, telemetry, detection, communicator, config)
        c2 = C2Reactor(ps.execute_layer, data_store, message_dispatcher, telemetry)
        pd = PersonDetector(c2.execute_layer)
        bl = BatteryLifeChecker(pd.execute_layer, telemetry, int(config['engine']['speed']))
        cd = CollisionDetector(bl.execute_layer, data_store, telemetry)
        self.entry = cd.execute_layer
        self.c2_reactor = c2
        self.battery_life_checker = bl
        self.pit_stop = ps
    def run(self):
        start = time.clock()
        output = self.entry(Action())
        end = time.clock()
        t = end - start
        if t > 1:
            print("WARNING: reactor took more than 1 second to complete")
        return output
