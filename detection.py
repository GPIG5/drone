import aiofiles
import asyncio
import base64
import time

from messages import PinorMesh

class Detection:
    def __init__(self, config, communicator, messagedispatcher):
        self.uuid = config.get('uuid')
        self.data_folder = config.get('data_folder')
        self.pinor_file = self.data_folder + 'pinor.csv'
        self.communicator = communicator
        self.messagedispatcher = messagedispatcher
        self.pinor = []

    @asyncio.coroutine
    def initialise(self):
        f = yield from aiofiles.open(self.pinor_file, mode='w')
        try:
            yield from f.write('timestamp,lat,lon,alt,img\n')
        finally:
            yield from f.close()

    @asyncio.coroutine
    def startup(self):
        while True:
            msg = yield from self.messagedispatcher.wait_for_message('direct', 'pinor').to_json()

            timestamp = time.time()
            timestr = time.strftime('%Y%m%d%H%M%S')
            pinor = (timestamp, msg['data']['pinor'])
            img64 = msg['data']['img']

            # Write image to file
            f = yield from aiofiles.open(self.data_folder + 'images/' + timestr + '.jpg', mode='w')
            try:
                yield from f.write(base64.decodestring(img))
            finally:
                yield from f.close()

            # Write co-ords to file
            f = yield from aiofiles.open(self.pinor_file, mode='w')
            try:
                for pinor in msg['data']['pinor']:
                    point = pinor.to_json()
                    yield from f.write(timestamp + ',' + point['lat'] + ',' + point['lon'] + ',' + point['alt'] + ',' + timestr + '.jpg' + '\n')
            finally:
                yield from f.close()

            self.pinor.append(pinor)
            yield from self.communicator.send(PinorMesh(self.uuid, self.uuid, pinor).to_json())

    def get_pinor():
        return self.pinor
