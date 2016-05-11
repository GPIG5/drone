
import asyncio
import configparser
from enum import Enum
import uuid

from communicator import Communicator
from datastore import Datastore
from detection import Detection
from messagedispatcher import Messagedispatcher
from navigator import Navigator
from telemetry import Telemetry

class Drone:
	def __init__(self, config):
		self.uuid = uuid.uuid4()
		self.config = config
		comconf = self.config["communicator"]
		self.communicator = Communicator(comconf["host"], comconf["port"], self.uuid)
		self.messagedispatcher = Messagedispatcher(self.communicator)
		self.datastore = Datastore(self.messagedispatcher)
		self.detection = Detection(self.messagedispatcher)
		self.navigator = Navigator(self.messagedispatcher)
		self.telemetry = Telemetry(self.messagedispatcher)

	def getUUID(self):
		return self.uuid

	def getConfig(self, key = None):
		if key is None:
			return self.config
		elif key in self.config:
			return self.config[key]
		else:
			raise KeyError('Key: ' + key + ' not found in configuration.')

	@asyncio.coroutine
	def startup(self):
		yield from self.communicator.initialise()

	def run(self):
		tasks = [
			self,
			self.datastore,
			self.detection,
			self.messagedispatcher,
			self.navigator,
			self.telemetry
		]
		loop = asyncio.get_event_loop()
		print("starting tasks")
		loop.run_until_complete(asyncio.wait([asyncio.async(x.startup()) for x in tasks]))
		loop.close()


def main():
	config = configparser.ConfigParser()
	config.read('config.ini')

	drone = Drone(config)
	drone.run()

if __name__ == "__main__":
	# execute only if run as a script
	main()
