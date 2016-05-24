import aiofiles
import asyncio
import base64
import os
import time

from messages import PinorMesh

class Detection:
    def __init__(self, config, communicator, messagedispatcher):
        self.uuid = config.get('uuid')
        self.data_folder = config.get('data_folder') + config.get('uuid') + '/'
        self.pinor_file = self.data_folder + 'pinor.csv'
        self.image_folder = self.data_folder + 'images/'
        self.communicator = communicator
        self.messagedispatcher = messagedispatcher

    @asyncio.coroutine
    def initialise(self):
        if not os.path.isdir(self.image_folder):
           os.makedirs(self.image_folder)

        f = yield from aiofiles.open(self.pinor_file, mode='w')
        try:
            yield from f.write('timestamp,lat,lon,alt,img\n')
        finally:
            yield from f.close()

    @asyncio.coroutine
    def startup(self):
        while True:
            msg = yield from self.messagedispatcher.wait_for_message('direct', 'pinor')

            timestamp = str(time.time())
            timestr = time.strftime('%Y%m%d%H%M%S')

            # Write image to file
            f = yield from aiofiles.open(self.image_folder + timestr + '.jpg', mode='wb')
            try:
                yield from f.write(base64.decodestring(msg.img.encode()))
            finally:
                yield from f.close()

            # Write co-ords to file
            f = yield from aiofiles.open(self.pinor_file, mode='a')
            try:
                for pinor in msg.pinor:
                    point = pinor.to_json()
                    yield from f.write(timestamp + ',' + str(point['lat']) + ',' + str(point['lon']) + ',' + str(point['alt']) + ',' + timestr + '.jpg' + '\n')
            finally:
                yield from f.close()

            yield from self.communicator.send_message(PinorMesh(self.uuid, self.uuid, msg.pinor))

    def get_pinor(self):
        return self.pinor
