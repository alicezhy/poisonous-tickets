# NOTICE: The Whole codebase is run under Python 3
"""
	This file is the entry point of the whole project. Run this script to conduct experiments on given strategy.
	Here are the arguments for command-line run:
		-l: Counselor to use. Default to "first_come_first_serve".
		-d: Directory of the trains to use. Default to "./Jinghu-All/"
		-c: Capacity per train. Default to 1000.
		-s: (Expected) Number of requests we get from passengers. It is a multiplier of the total capacity of all trains. Default to 3.0.
		-p: Power type of the railway system. Default to 1.
		-m: Mode = "s" (for single) or "m" (for multiple), representing whether we're working on a single railway (though potentially multiple trains) or a system of railways. Notice that different mode may result in different distributions of railway ticket demands.
		
"""

import sys
sys.path.append("./counselors/")
import random
import math
import json
import numpy as np
from Railway_system import Railway_system

# Generate a request of ticket assuming that we're working on a single railway (with potentially multiple trains)
class Request_generator:
	def __init__(self, railway_system):
		self.connected_pairs = []
		self.connected_pairs_prob = []
		for pair in railway_system.pairs_connectivity:
			self.connected_pairs.append(pair)
			self.connected_pairs_prob.append(railway_system.stations_info[str(pair[0])]["population"] * \
											 railway_system.stations_info[str(pair[1])]["population"])
		sm = np.sum(self.connected_pairs_prob) * 1.0
		self.connected_pairs_prob = list(np.array(self.connected_pairs_prob) / sm)

	def generate_request_single_mode(self):
		l = len(self.connected_pairs)
		result = self.connected_pairs[np.random.choice(range(l), p=self.connected_pairs_prob)]
		return result[0], result[1]


# Main function of Experiment
def counduct_experiment(railway_system, num_requests, verbose=False):
	request_generator = Request_generator(railway_system)
	for count in range(num_requests):
		# Generate a request
		x, y = request_generator.generate_request_single_mode()
		# Look at all choices - a list of (train, price)
		all_choices = railway_system.get_ticket_availability(x, y)
		if len(all_choices) == 0:
			result, price = railway_system.respond_to_request(None, x, y)
		else:
			# Pick a ticket according to price
			trains = []
			trains_prob = []
			min_price = min([c[1] for c in all_choices])
			for pair in all_choices:
				trains.append(pair[0])
				trains_prob.append((math.e ** (-pair[1] * 2.0 / min_price)))
			sm = np.sum(trains_prob) * 1.0
			trains_prob = list(np.array(trains_prob) / sm)
			selected_train = np.random.choice(trains, p=trains_prob)
			result, price = railway_system.respond_to_request(selected_train, x, y)
			if result:
				for pair in all_choices:
					if pair[0] == selected_train:
						assert (pair[1] == price)
		if verbose:
			name_start = railway_system.stations_info[str(x)]["name"]
			name_end = railway_system.stations_info[str(y)]["name"]
			if result:
				print ("Request #%d: ticket from %s to %s; result Accepted, on train %s with price %.2lf paid." % \
					(count, name_start, name_end, selected_train, price))
			else:
				print ("Request #%d: ticket from %s to %s; result Rejected." % \
					(count, name_start, name_end))
	efficiency, fairness = railway_system.calculate_efficiency_and_fairness()
	return efficiency, fairness, railway_system.request_records

if __name__ == "__main__":
	# Parse all arguments
	counselor_name = "first_come_first_serve"
	train_data_dir = "./Jinghu-All/"
	capacity_per_train = 1000
	num_requests_coef = 4.0
	power_type = 1
	mode = "s"

	num_args = len(sys.argv)
	for i in range(1, num_args): # Ignore sys.argv[0]
		if sys.argv[i] == "-l": counselor_name = sys.argv[i + 1]
		if sys.argv[i] == "-d": train_data_dir = sys.argv[i + 1]
		if sys.argv[i] == "-c": capacity_per_train = int(sys.argv[i + 1])
		if sys.argv[i] == "-s": num_requests_coef = float(sys.argv[i + 1])
		if sys.argv[i] == "-p": power_type = int(sys.argv[i + 1])
		if sys.argv[i] == "-m": mode = sys.argv[i + 1]

	# Load the railway system and counselor
	counselor = __import__(counselor_name).counselor
	railway_system = Railway_system(train_data_dir, capacity_per_train, power_type, mode, counselor)

	# conduct experiment
	num_trains = len(railway_system.trains_name)
	num_requests = int(round(num_requests_coef * capacity_per_train * num_trains))
	efficiency, fairness, requests_recod = counduct_experiment(railway_system, num_requests, True)
	print ("Strategy: %s; efficiency = %.3lf, fairness = %.3lf" % (counselor_name, efficiency, fairness))