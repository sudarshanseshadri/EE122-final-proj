###Use python 2.7 please!
import random
import math

secondsPerIter = 1e-3 #each iteration is 1 ms

class Packet(object):
	pack_id = 0
	def __init__(self, size):
		self.id = Packet.pack_id
		Packet.pack_id += 1
		self.size = size

	def size(self):
		return self.size

class PacketStream(object):
	### constructor for combination of many different streams for different packet sizes
	### for basic, call: <PacketStream([10], ]0.5])> to create a stream with packet size 10 that will produce a packet on each iter with p = 0.5
	def __init__(self, packetSizeList, paramsList):
		self.packetSizeList = packetSizeList
		self.paramsList = paramsList

	### from the internal packet streams, return either a total of 0 or 1 packets.
	def producePacket(self):
		#basic implementation has just one stream
		if random.random() < self.paramsList[0]:
			return Packet(self.packetSizeList[0]) 
		else:
			return None

class Router(object):
	### for basic, call: <Router([Queue1, Queue2], [0.5, 0.5])> to have router send to Queue1 and Queue1 with probability 1/2 each (at the start).
	def __init__(self, outgoingQueueList, initialParamsList):
		assert len(outgoingQueueList) == len(initialParamsList)
		assert len(outgoingQueueList) > 1
		assert math.fabs(sum(initialParamsList)-1) < 1e-16 #assert that the initial probabilot list sums to about 1
		self.outgoingQueueList = outgoingQueueList
		self.paramsList = initialParamsList

	#process the received packet (recv) by sending it to any of the queues in the outgoingQueueList
	def dispatch(self, recv):
		thresh = random.random()
		count = 0
		for i in range(len(self.outgoingQueueList)):
			count += self.paramsList[i]
			if count >= thresh:
				if self.outgoingQueueList[i].push(recv):
					print "packet pushed to queue {}".format(i)
				else:
					print "packet dropped by queue {}".format(i)
				return
		raise Exception("Error in internal probability list:\n" + self.paramsList)

class Queue(object):
	def __init__(self, capacity, param):
		self.capacity = capacity
		self.buff = []
		self.param = param

	def push(self, packet):
		if len(self.buff) < self.capacity:
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
		return None 

#main loop:
num_iter = 10
ps = PacketStream([10], [0.6])
qList = [Queue(5, .3), Queue(3, .5)]
r = Router(qList, [.5, .5])
for i in xrange(num_iter):
	print "iter {}:".format(i)
	newPacket = ps.producePacket()
	if newPacket is not None:
		r.dispatch(newPacket)
	# dispatchedPackets = [q.dispatch() for q in qList]
	# print dispatchedPackets
print "Simulation finished"