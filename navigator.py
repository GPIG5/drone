import asyncio

import datastore
from messages import GridMesh, UploadDirect
from point import Point
from reactor import Reactor

class Navigator:
    def __init__(self, config, data_store, telemetry, messagedispatcher, communicator, detection):
        self.uuid = config.get('DEFAULT', 'uuid')
        self.debug = 'True' == config.get('DEFAULT', 'debug')
        self.data_store = data_store
        self.messagedispatcher = messagedispatcher
        self.communicator = communicator
        self.reactor = Reactor(config, data_store, telemetry, messagedispatcher, communicator, detection)
        self.current_target = Point(
            latitude = telemetry.get_location().latitude,
            longitude = telemetry.get_location().longitude,
            altitude = telemetry.get_location().altitude
        )

    @asyncio.coroutine
    def startup(self):
        while True:
            action = self.reactor.run()
            grid = self.data_store.get_grid_state()
            if action is not None:
                if action.has_move():
                    self.current_target = action.move
                    if self.current_target.altitude < 10:
                        self.current_target.altitude = 100
                if action.has_claim_sector():
                    grid.set_state_for(action.claim_sector, datastore.SectorState.being_searched, self.uuid)
                if action.has_complete_sector():
                    grid.set_state_for(action.complete_sector, datastore.SectorState.searched, self.uuid)
                if (self.debug or self.current_target.altitude < 10) and action.has_move_info():
                    print(action.move_info)

            if grid is not None:
                yield from self.communicator.send_message(GridMesh(self.uuid, self.uuid, grid))

            yield from asyncio.sleep(1)

    def get_current_target(self):
        return self.current_target
