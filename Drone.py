
from enum import Enum
import uuid

class State(Enum):
    wait = 1
    search = 2
    found = 3
    battery = 4

class Drone:
    def __init__(self):
        self.uuid = uuid.uuid4()
        self.state = State.wait
        self.location
        self.battery
        self.comms

    def run():
        pass

def main():
    drone = Drone()
    drone.run()

if __name__ == "__main__":
    # execute only if run as a script
    main()
