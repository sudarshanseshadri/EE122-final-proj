###Use python 2.7 please!
import random
from collections import defaultdict 

import numpy as np
from numpy.linalg import norm
import matplotlib.pyplot as plt

iter_initialize = 1000
iter_per_update = 100

def is_update_iter():
	return (curr_iter > iter_initialize) and (curr_iter % iter_per_update == 0)

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
	def __init__(self, outgoingQueueList, initialProbsList, opt_delay, mult_pow, memMult):
		assert len(outgoingQueueList) == len(initialProbsList)
		assert len(outgoingQueueList) > 1
		self.outgoingQueueList = outgoingQueueList
		self.probsList = normalize(np.array(initialProbsList))
		self.packetsSeen = 0
		self.packetsLost = 0
		self.packetsLostListTotal = [0.0, 0.0]
		self.packetsLostListUpdate = [0.0, 0.0]
		self.packetsSentListTotal = [0.0, 0.0]
		self.packetsSentListUpdate = [0.0, 0.0]

		self.q1_delay = None
		self.q2_delay = None

		self.opt_delay = opt_delay
		self.mult_pow = mult_pow
		self.memMult = memMult

	def update(self):
		if self.opt_delay:
			if self.q1_delay is None or self.q2_delay is None: return
			if self.q1_delay == 0: self.q1_delay = 1
			if self.q2_delay == 0: self.q2_delay = 1
			m = np.power(self.q1_delay / float(self.q2_delay), 1.0/self.mult_pow)
			# print self.q1_delay, self.q2_delay
			# print self.probsList, m
		else:
			q1_drop_prop = self.packetsLostListUpdate[0] / float(self.packetsSentListUpdate[0])
			if q1_drop_prop == 0: return
			q2_drop_prop = self.packetsLostListUpdate[1] / float(self.packetsSentListUpdate[1])
			if q2_drop_prop == 0: return
			m = np.power(q1_drop_prop / float(q2_drop_prop), 1.0/self.mult_pow)
			memMult = 1.5
			for i in range(len(self.packetsSentListUpdate)):
				self.packetsLostListUpdate[i] /= memMult
				self.packetsSentListUpdate[i] /= memMult
		self.probsList = normalize(np.array([self.probsList[0] / float(m), self.probsList[1] * float(m)]))


	#process the received packet (recv) by sending it to any of the queues in the outgoingQueueList
	def dispatch(self, recv):
		if recv is None: return
		self.packetsSeen += 1
		thresh = random.random()
		count = 0
		if is_update_iter():
			self.update()
		for i in range(len(self.outgoingQueueList)):
			count += self.probsList[i]
			if count >= thresh:
				self.packetsSentListTotal[i] += 1
				self.packetsSentListUpdate[i] += 1
				if self.outgoingQueueList[i].push(recv):
					return
				else:
					self.packetsLost += 1
					self.packetsLostListTotal[i] += 1
					self.packetsLostListUpdate[i] += 1
				return
		raise Exception("Error in internal probability list:\n" + self.probsList)

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
		self.delay_list_by_queue = [[], []]

	def snoop(self, packet, queue_index):
		delay_iters = packet.recv_iter - packet.start_iter
		delay_list = self.delay_list_by_queue[queue_index]
		delay_list.insert(0, delay_iters)
		if len(delay_list) > self.delay_list_max_size:
			self.delay_list_by_queue[queue_index] = delay_list[:self.delay_list_max_size]

	def calc_delay(self, queue_index):
		delay_list = self.delay_list_by_queue[queue_index]
		if delay_list == []: return 0
		return sum(delay_list) / float(len(delay_list))

	def broadcast(self, router):
		if is_update_iter():
			router.q1_delay = self.delay_list_by_queue[0][-1]
			router.q2_delay = self.delay_list_by_queue[1][-1]

def run_test(max_iter, pck_rate, q_len_list, q_rate_list, rout_prob_list, perf_analyzer_size, opt_delay=True, mult_pow=25, memMult=1.5):
	assert len(q_len_list) == len(q_rate_list)
	
	global curr_iter
	curr_iter = 0

	ps = PacketStream(pck_rate)
	qList = [Queue(q_len_list[i], q_rate_list[i]) for i in range(len(q_len_list))]
	r = Router(qList, rout_prob_list, opt_delay, mult_pow, memMult)
	pa = PerformanceAnalyzer(perf_analyzer_size)

	delay_list = [[],[]]
	prob_list = []
	for curr_iter in xrange(max_iter):
		newPacket = ps.producePacket()
		r.dispatch(newPacket)
		dispatchedPackets = [q.dispatch() for q in qList]
		for i in range(len(dispatchedPackets)):
			if dispatchedPackets[i] is not None: 
				pa.snoop(dispatchedPackets[i], i)
		for i in range(2):
			delay_list[i].append(pa.calc_delay(i))
		pa.broadcast(r)
		prob_list.append(r.probsList[0])

	print "Simulation finished"
	print "Packets lost", r.packetsLostListTotal
	print "Proportion of packets dropped: {}".format(r.packetsLost / float(r.packetsSeen))
	average_delay_q1 = sum(delay_list[0])/float(len(delay_list[0]))
	average_delay_q2 = sum(delay_list[1])/float(len(delay_list[1]))
	print "Average delay", average_delay_q1, average_delay_q2
	print "Final router probs: {}".format(r.probsList)
	print "\n"
	return [average_delay_q1, average_delay_q2, r.packetsSentListTotal, r.packetsLostListTotal]

#main loop:
p_list = np.arange(0.05, 1.0, 0.05)
memMultList = np.arange(1.0, 4.25, 0.25)



pck_rate = 0.05
q_len_list = [10, 10]
q_rate_list = [0.03, 0.04]
starting_prob_list = [0.5, 0.5]

info_title = "pck_rate={}_len_list={}_q_rate_list={}".format(pck_rate, q_len_list, q_rate_list)

for _ in range(10):
	results = run_test(int(1e5), pck_rate, q_len_list, q_rate_list, starting_prob_list, 100)

# delay_list = [[], []]
# q1_lost_list = []
# q2_lost_list = []
# for p in p_list:
# 	num_iter = 10
# 	delay_list_help = [[], []]
# 	q1_lost_list_help = []
# 	q2_lost_list_help = []
# 	for _ in xrange(num_iter):
# 		results = run_test(int(1e5), pck_rate, q_len_list, q_rate_list, [p, 1-p], 100)
# 		for i in range(2): 		
# 			delay_list_help[i].append(results[i])
# 			q1_lost_list_help.append(results[2][0] / float(results[1]))
# 			q2_lost_list_help.append(results[2][1] / float(results[1]))		
# 		for i in range(2):
# 			delay_list[i].append(sum(delay_list_help[i])/float(num_iter))
# 	q1_lost_list.append(sum(q1_lost_list_help)/float(num_iter))
# 	q2_lost_list.append(sum(q2_lost_list_help)/float(num_iter))

# plt.plot(p_list, delay_list)
# plt.title("Delay in iterations vs prob. of sending to Q1")
# plt.savefig("Delay_with_{}.png".format(info_title))
# plt.show()
# # plt.close()

# plt.plot(p_list, q1_lost_list)
# plt.title("Proportion of packets dropped by Q1 vs prob. of sending to Q1")
# plt.savefig("Q1_drop_rate_with_{}.png".format(info_title))
# plt.show()
# # plt.close()

# plt.plot(p_list, q2_lost_list)
# plt.title("Proportion of packets dropped by Q2 vs prob. of sending to Q1")
# plt.savefig("Q2_drop_rate_with_{}.png".format(info_title))
# plt.show()
# # plt.close()
