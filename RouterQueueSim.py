###Use python 2.7 please!
import random
from collections import defaultdict 

import numpy as np
from numpy.linalg import norm
import matplotlib.pyplot as plt

class Packet(object):
	def __init__(self):
		self.start_iter = curr_iter
		self.recv_iter = None

class PacketStream(object):
	### constructor for packet stream
	### for basic, call: <PacketStream(0.5)> to create a stream that produces a packet on each iter with p = 0.5
	def __init__(self, rate):
		self.rate = rate

	### from the internal packet streams, return either a total of 0 or 1 packets.
	def producePacket(self):
		#basic implementation has just one stream
		if random.random() < self.rate:
			return Packet() 
		else:
			return None

def normalize(v):
	return v / norm(v, ord=1)

class Router(object):
	### for basic, call: <Router([Queue1, Queue2], [0.5, 0.5])> to have router send to Queue1 and Queue1 with probability 1/2 each (at the start).
	def __init__(self, outgoingQueueList, initialProbsList):
		assert len(outgoingQueueList) == len(initialProbsList)
		assert len(outgoingQueueList) > 1
		self.outgoingQueueList = outgoingQueueList
		self.probsList = normalize(np.array(initialProbsList))
		self.packetsSeen = 0
		self.packetsLost = 0
		self.packetsLostDict = defaultdict(lambda: 0)

		self.probsDeltaList = None
		self.delayMemList = []

	def update(self, loss_index=None):
		# self.probsDeltaList = update_delta_list(self.probsDeltaList)
		# self.probsList += self.probsDeltaList
		pass

	#process the received packet (recv) by sending it to any of the queues in the outgoingQueueList
	def dispatch(self, recv):
		if recv is None: return
		self.packetsSeen += 1
		thresh = random.random()
		count = 0
		# if curr_iter % 10 == 0:
		# 	self.update()
		for i in range(len(self.outgoingQueueList)):
			count += self.probsList[i]
			if count >= thresh:
				if self.outgoingQueueList[i].push(recv):
					return
				else:
					self.packetsLost += 1
					self.packetsLostDict[i] += 1
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
		if self.size() > 0 and random.random() < self.param:
			outputPack = self.pop()
			outputPack.recv_iter = curr_iter
			return outputPack
		else:
			return None

class PerformanceAnalyzer(object):
	def __init__(self, n):
		self.delay_list_max_size = n
		self.delay_list = []

	def snoop(self, packet):
		delay_iters = packet.recv_iter - packet.start_iter
		self.delay_list.insert(0, delay_iters)
		if len(self.delay_list) > self.delay_list_max_size:
			self.delay_list = self.delay_list[:self.delay_list_max_size]

	def calc_delay(self):
		if self.delay_list == []: return 0
		return sum(self.delay_list) / float(len(self.delay_list))

def run_test(max_iter, pck_rate, q_len_list, q_rate_list, rout_prob_list, perf_analyzer_size):
	assert len(q_len_list) == len(q_rate_list)
	
	global curr_iter
	curr_iter = 0

	ps = PacketStream(pck_rate)
	qList = [Queue(q_len_list[i], q_rate_list[i]) for i in range(len(q_len_list))]
	r = Router(qList, rout_prob_list)
	pa = PerformanceAnalyzer(perf_analyzer_size)

	delay_list = []
	prob_list = []
	for curr_iter in xrange(max_iter):
		newPacket = ps.producePacket()
		r.dispatch(newPacket)
		dispatchedPackets = [q.dispatch() for q in qList]
		for dp in dispatchedPackets:
			if dp is not None: pa.snoop(dp)

		delay_list.append(pa.calc_delay())
		prob_list.append(r.probsList[0])

	print "Simulation finished"
	print r.packetsLostDict
	print "Proportion of packets dropped: {}".format(r.packetsLost / float(r.packetsSeen))
	average_delay = sum(delay_list)/float(len(delay_list))
	print average_delay
	print "Final router probs: {}".format(r.probsList)
	return [average_delay, r.packetsSeen, r.packetsLostDict]

#main loop:
p_list = np.arange(0.05, 1.0, 0.05)
delay_list = []
q1_lost_list = []
q2_lost_list = []

pck_rate = 0.05
q_len_list = [10, 10]
q_rate_list = [0.035, 0.035]

for p in p_list:
	num_iter = 10
	delay_list_help = []
	q1_lost_list_help = []
	q2_lost_list_help = []
	for _ in xrange(num_iter):
		results = run_test(int(1e5), pck_rate, q_len_list, q_rate_list, [p, 1-p], 100)
		delay_list_help.append(results[0])
		q1_lost_list_help.append(results[2][0] / float(results[1]))
		q2_lost_list_help.append(results[2][1] / float(results[1]))		
	delay_list.append(sum(delay_list_help)/float(num_iter))
	q1_lost_list.append(sum(q1_lost_list_help)/float(num_iter))
	q2_lost_list.append(sum(q2_lost_list_help)/float(num_iter))

info_title = "pck_rate={}_len_list={}_q_rate_list={}".format(pck_rate, q_len_list, q_rate_list)

plt.plot(p_list, delay_list)
plt.title("Delay in iterations vs prob. of sending to Q1")
# plt.savefig("Delay_with_{}.png".format(info_title))
plt.show()
# plt.close()

plt.plot(p_list, q1_lost_list)
plt.title("Proportion of packets dropped by Q1 vs prob. of sending to Q1")
# plt.savefig("Q1_drop_rate_with_{}.png".format(info_title))
plt.show()
# plt.close()

plt.plot(p_list, q2_lost_list)
plt.title("Proportion of packets dropped by Q2 vs prob. of sending to Q1")
# plt.savefig("Q2_drop_rate_with_{}.png".format(info_title))
plt.show()
# plt.close()
