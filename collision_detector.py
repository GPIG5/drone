from layer import *


class CollisionDetector(Layer):
    def __init__(self, next, data_store, telemetry):
        Layer.__init__(self, next)
        self.data_store = data_store
        self.telemetry = telemetry

    def execute_layer(self, current_output):
        op = Layer.execute_layer(self, current_output)
        collide = None
        collide_dist = None
        for uuid, drone in self.data_store.all_drones().items():
            d = drone.location.distance_to(self.telemetry.get_location())
            if collide is None or d < collide_dist:
                collide = drone.location
                collide_dist = d
        if collide is not None and collide_dist <= 10:
            op.move = self.telemetry.get_location().perp(collide, 10 / max(collide_dist, 1))
            if hasattr(current_output.move, 'simple_string'):
                op.move_info = "COLLISION DETECTION MOVE TO: " + op.move.simple_string()
            else:
                op.move_info = "COLLISION DETECTION MOVE TO"
        return op
