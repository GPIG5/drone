from point import Point

class Layer:
    def __init__(self, next):
        self.next = next
    def execute_layer(self, current_output):
        current_output = self.next(current_output)
        return current_output

class Action:
    def __init__(self, move = None, take_picture = None, claim_sector = None):
        self.move = move
        self.take_picture = take_picture
        self.claim_sector = claim_sector
    def has_move(self):
        return self.move != None
    def has_take_picture(self):
        return self.take_picture != None
    def has_claim_sector(self):
        return self.claim_sector != None