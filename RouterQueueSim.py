secondsPerIter = 1e-3 #each iteration is 1 ms

class Packet(object):
	def __init__(self, size):
		self.size = size

	def size(self):
		return self.size

class PacketStream(object):
	### constructor for combination of many different streams for different packet sizes
	### for basic, call: <PacketStream([10], ["geom"], [0.5])> to create a stream with packet size 10 that will produce a packet on each iter with p = 0.5
	def __init__(self, packetSizeList, distTypeList, distParamsList):
		self.packetSizeList = packetSizeList
		self.distTypeList = distTypeList
		self.distParamsList = distParamsList

	### from the internal packet streams, return either a total of 0 or 1 packets.
	def producePackets(self):
		"""IMPLEMENT ME"""

class Router(object):
	### for basic, call: <Router([Queue1, Queue2], [0.5, 0.5])> to have router send to Queue1 and Queue1 with probability 1/2 each (at the start).
	def __init__(self, outgoingQueueList, initialParamsList):
		self.outgoingQueueList = outgoingQueueList
		self.initialParamsList = initialParamsList

	#process the received packet (recv) by sending it to any of the queues in the outgoingQueueList
	def dispatch(self, recv=None): 
		"""IMPLEMENT ME"""

class Queue(object):
	def __init__(self, capacity, distType, paramType):
		self.capacity = capacity
		self.buff = []

	def push(self, packet):
		if len(self.buff) + 1 < self.capacity:
			self.buff = [packet] + self.buff
			return True
		else:
			return False

	def pop(self):
		if self.buff != []:
			return self.buff.pop()
		else:
			return None

	def size(self):
		return len(self.buff)

	#dispatches 0 or 1 packets
	def dispatch(self):
		"""IMPLEMENT ME""" 
		