import asyncio

class Navigator:
	def __init__(self, messagedispatcher):
		self.messagedispatcher = messagedispatcher

	@asyncio.coroutine
	def startup(self):
		pass
