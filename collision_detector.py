from layer import *

class Collision_detector(Layer):
    def __init__(self, next):
        Layer.__init__(self, next)
    def execute_layer(self, current_output):
        return Layer.execute_layer(self, current_output)
