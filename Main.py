
import asyncio
import DataStore
import Detection
import Drone
import Navigator
import Telemetry
import MessageDispatcher

tasks = [
	DataStore,
	Detection,
	Drone,
	Navigator,
	Telemetry,
	MessageDispatcher
]

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait([asyncio.async(x.startup()) for x in tasks]))
loop.close()
