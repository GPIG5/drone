from layer import *
import importlib
from collision_detector import Collision_detector
from battery_life_checker import Battery_life_checker
from person_detector import Person_detector
from c2_reactor import C2_reactor
from sector_controller import Sector_controller
from swarm_controller import Swarm_controller

id = lambda x: x

class Reactor:
    def __init__(self, telemetry):
        swc = Swarm_controller(id)
        secc = Sector_controller(swc.execute_layer)
        c2 = C2_reactor(secc.execute_layer)
        pd = Person_detector(c2.execute_layer)
        bl = Battery_life_checker(pd.execute_layer, telemetry)
        cd = Collision_detector(bl.execute_layer)
        self.entry = cd.execute_layer
    def run(self):
        return self.entry(Action())
