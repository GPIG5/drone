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
    def __init__(self, telemetry):
        swc = SwarmController(id)
        secc = SectorController(swc.execute_layer)
        c2 = C2Reactor(secc.execute_layer)
        pd = PersonDetector(c2.execute_layer)
        bl = BatteryLifeChecker(pd.execute_layer, telemetry)
        cd = CollisionDetector(bl.execute_layer)
        self.entry = cd.execute_layer
    def run(self):
        return self.entry(Action())
