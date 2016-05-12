from layer import *

class Battery_life_checker(Layer):
    def __init__(self, next, telemetry):
        Layer.__init__(self, next)
        self.telemetry = telemetry
    def execute_layer(self, current_output):
        op = Layer.execute_layer(self, current_output)
        if self.telemetry.getBattery() < (self.telemetry.getInitialBattery() / 2):
            op.move = self.telemetry.getInitialLocation()
        return op
