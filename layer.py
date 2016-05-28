from point import Point


class Layer:
    def __init__(self, next):
        self.next = next

    def execute_layer(self, current_output):
        current_output = self.next(current_output)
        return current_output


class Action:
    def __init__(self, move=None, take_picture=None, claim_sector=None, complete_sector=None, send_data=None):
        self.move = move
        self.take_picture = take_picture
        self.claim_sector = claim_sector
        self.complete_sector = complete_sector
        self.send_data = send_data

    def has_move(self):
        return self.move is not None

    def has_take_picture(self):
        return self.take_picture is not None

    def has_claim_sector(self):
        return self.claim_sector is not None

    def has_complete_sector(self):
        return self.complete_sector is not None

    def has_send_data(self):
        return self.send_data is not None
