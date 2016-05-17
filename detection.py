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

    @asyncio.coroutine
    def initialise(self):
        f = yield from aiofiles.open(self.pinor_file, mode='w')
        try:
            yield from f.write('timestamp,lon,lat,alt,img\n')
        finally:
            yield from f.close()

    @asyncio.coroutine
    def startup(self):
        while True:
            msg = yield from self.messagedispatcher.wait_for_message('direct', 'pinor')
            msg = msg.to_json()

            timestr = time.strftime('%Y%m%d%H%M%S')
            pinors = msg['data']['pinor']
            img64 = msg['data']['img']

            # Write image to file
            f = yield from aiofiles.open(self.data_folder + 'images/' + timestr + '.jpg', mode='wb')
            try:
                yield from f.write(base64.decodestring(img64.encode()))
            finally:
                yield from f.close()

            # Write co-ords to file
            f = yield from aiofiles.open(self.pinor_file, mode='w')
            try:
                for pinor in pinors:
                    point = pinor.to_json()
                    yield from f.write(timestamp + ',' + point['lon'] + ',' + point['lat'] + ',' + point['alt'] + ',' + timestr + '.jpg' + '\n')
            finally:
                yield from f.close()

            yield from self.communicator.send(PinorMesh(self.uuid, self.uuid, pinors).to_json())

    def get_pinor():
        return self.pinor
