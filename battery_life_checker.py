from layer import *

class BatteryLifeChecker(Layer):
    def __init__(self, next, telemetry):
        Layer.__init__(self, next)
        self.telemetry = telemetry
    def execute_layer(self, current_output):
        op = Layer.execute_layer(self, current_output)
        if self.telemetry.get_battery() < (self.telemetry.get_initial_battery() / 2):
            op.move = self.telemetry.get_initial_location()
        return op
