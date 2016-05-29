import asyncio

import datastore
from messages import ClaimMesh, CompleteMesh, UploadDirect
from point import Point
from reactor import Reactor

class Navigator:
    def __init__(self, config, data_store, telemetry, communicator, engine, **kwargs):
        self.uuid = config['uuid']
        self.data_store = data_store
        self.communicator = communicator
        self.engine = engine
        self.telemetry = telemetry
        self.reactor = Reactor(
            config=config,
            data_store=data_store,
            telemetry=telemetry,
            communicator=communicator,
            engine=engine,
            **kwargs
        )
        self.engine.set_current_target(Point(
            latitude = self.telemetry.get_location().latitude,
            longitude = self.telemetry.get_location().longitude,
            altitude = self.telemetry.get_location().altitude
        ))


    @asyncio.coroutine
    def startup(self):
        yield from asyncio.gather(self.reactor.startup(), self.navstartup())
    @asyncio.coroutine
    def initialise(self):
        yield from self.reactor.initialise()

    @asyncio.coroutine
    def navstartup(self):
        while True:
            action = self.reactor.run()
            if action is not None:
                if action.has_move():
                    self.set_current_target(action.move)
                if action.has_claim_sector():
                    grid = self.data_store.get_grid_state()
                    grid.set_state_for(action.claim_sector, datastore.SectorState.being_searched)
                    msg = ClaimMesh(self.uuid, self.uuid, action.claim_sector, grid.get_sector_space(action.claim_sector))
                    yield from self.communicator.send_message(msg)
                if action.has_complete_sector():
                    grid = self.data_store.get_grid_state()
                    grid.set_state_for(action.complete_sector, datastore.SectorState.searched)
                    msg = CompleteMesh(self.uuid, self.uuid, action.complete_sector, grid.get_sector_space(action.complete_sector))
                    yield from self.communicator.send_message(msg)
                if action.has_send_data():
                    yield from self.communicator.send_message(UploadDirect(self.uuid, action.send_data))

            yield from asyncio.sleep(1)

    def get_current_target(self):
        return self.engine.get_current_target()

    def set_current_target(self, ct):
        return self.engine.set_current_target(ct)
