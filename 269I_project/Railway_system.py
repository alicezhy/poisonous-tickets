import numpy as np
import os
import copy
import json

"""
	Here are (some of) the members of a Railway_system class:
	------------- Properties ------------
	- self.power_type
	- self.mode
	- self.counselor: a function that is provided externally
	- self.capacity_per_train
	- self.trains_name
	- self.trains_info
	- self.trains_capacity_per_block
	- self.trains_interval_prices
	- self.trains_interval_original_prices
	- self.pairs_connectivity
	- self.stations_info
	- self.request_records: a list of all the requests. Each request record is a dict with "train", "start_station", "end_station", "price", "original_price". If price is -1, that means the request is rejected because of no available resource. If price is -2, that means we reject the request despite available resource (power_type = 1 must hold in this case). Otherwise, it's the price traded. "original_price" is equivalent to the distance between these two stations on the train specified.
	--------- Member functions ----------

"""
class Railway_system:
	"""
		- train_data_dir is a folder containing information of all trains
			There should be at least two files:
				- station_info.json, a JSON file mapping index to station info, including the name, passenger flow and geolocation of this station
				- TRAIN_NUMBER.npy (e.g. G7001.npy), a Numpy array with size N * 3; N indicates the number of stations, and each line is (station_index, distance_to_next_stop, time_to_next_stop). If there are multiple trains managed by the system, give multiple such files
		- capacity_per_train is the number of seats per train. Throughout the project, we assume that all trains have the same capacity, which is a reasonable approximation to the real situation.
		- power_type is an integer
			- power_type = 1 means the system have the right to reject a request, but not to modify the price
			- power_type = 2 means the system could modify the price, but not to reject a request if resource available
	"""
	def __init__(self, train_data_dir, capacity_per_train, power_type, mode, counselor):
		self.power_type = power_type
		self.mode = mode
		self.counselor = counselor
		self.capacity_per_train = capacity_per_train
		self.trains_name = []
		self.trains_info = {}
		self.trains_capacity_per_block = {}
		self.trains_interval_prices = {}
		self.pairs_connectivity = set()
		self.load_train_data(train_data_dir)
		self.trains_interval_original_prices = copy.deepcopy(self.trains_interval_prices)
		self.request_records = []
		# if self.power_type == 1:
		# 	# Check it is actually resource model 1
		# 	assert (len(self.trains_name) == 1)
		# 	train_name = self.trains_name[0]
		# 	train_info = self.trains_info[train_name]
		# 	for i in range(train_info.shape[0]):
		# 		assert (train_info[i, 0] == i + 1)

	# This function will load the train data to self.trains_name and self.trains_info
	# It will initialize self.trains_capacity_per_block and self.trains_interval_prices accordingly
	def load_train_data(self, train_data_dir):
		all_files = os.listdir(train_data_dir)
		assert ("stations_info.json" in all_files)
		for file in all_files:
			if file == "stations_info.json":
				with open(os.path.join(train_data_dir, file), "r") as f:
					self.stations_info = json.load(f)
			else:
				train_info = np.load(os.path.join(train_data_dir, file))
				train_name = file.split(".")[0]
				self.trains_name.append(train_name)
				self.trains_info[train_name] = train_info
				num_stations = train_info.shape[0]
				self.trains_capacity_per_block[train_name] = [self.capacity_per_train for i in range(num_stations)]
				prices = np.zeros((num_stations, num_stations))
				for i in range(num_stations - 1):
					sm = 0
					for j in range(i, num_stations - 1):
						sm += train_info[j][1] # column 1 is distance to next stop
						prices[i][j + 1] = sm
						self.pairs_connectivity.add((train_info[i, 0], train_info[j + 1, 0])) # Add pair of connected stations 
				self.trains_interval_prices[train_name] = prices

	def find_train_station_index(self, train, station):
		for i in range(self.trains_info[train].shape[0]):
			if self.trains_info[train][i, 0] == station: return i
		return None

	# Regardless of the capacity, check whether there's some train that has a ticket from start_station to end_station. The principle is that, if there's no train at all, this request is void and we re-generate; otherwise this request is legal and we reject it because of no capacity.
	# NOT IN USE
	def check_pair_connectivity(self, start_station, end_station):
		return (start_station, end_station) in self.pairs_connectivity

	# For a given interval, return a list of possible options - each term is (train_name, price)
	def get_ticket_availability(self, start_station, end_station):
		all_choices = []
		for train in self.trains_name:
			idx_start = self.find_train_station_index(train, start_station)
			idx_end = self.find_train_station_index(train, end_station)
			if (idx_start is not None) and (idx_end is not None) and (idx_start < idx_end):
				if min(self.trains_capacity_per_block[train][idx_start:idx_end]) > 0:
					all_choices.append((train, self.trains_interval_prices[train][idx_start, idx_end]))
		return all_choices
	
	# The request specifies a train. If train is None, that means no train could satisfy this request; we just add it to the record. Otherwise, actually check whether we will fulfill this request.
	def respond_to_request(self, train, start_station, end_station):
		if train is None:
			self.request_records.append({
				"start_station" : start_station,
				"end_station" : end_station,
				"price" : -1
			})
			return False, None
		idx_start = self.find_train_station_index(train, start_station)
		idx_end = self.find_train_station_index(train, end_station)
		if self.power_type == 1:
			# Consider whether to reject this request
			advice = self.counselor(self, train, idx_start, idx_end)
		else:
			# Must accept it
			advice = True
		price = None
		# Make the record for ticket requests
		if advice == True:
			price = self.trains_interval_prices[train][idx_start, idx_end]
			self.request_records.append({
				"train" : train,
				"start_station" : start_station,
				"end_station" : end_station,
				"price" : price,
				"original_price" : self.trains_interval_original_prices[train][idx_start, idx_end]
			})
			for i in range(idx_start, idx_end):
				self.trains_capacity_per_block[train][i] -= 1
			# Update the prices according the counselor (it will directly modify it)
			if self.power_type == 2:
				self.counselor(self, train, idx_start, idx_end)
		else:
			self.request_records.append({
				"start_station" : start_station,
				"end_station" : end_station,
				"price" : -1
			})
		return advice, price

	def calculate_efficiency_and_fairness(self):
		total_resource = 0 # total mileages of all trains
		for train in self.trains_name:
			train_info = self.trains_info[train]
			c = train_info.shape[0]
			total_resource += np.sum(train_info[:, 1]) * self.capacity_per_train
		# Calculate efficiency
		used_resource = 0
		for request in self.request_records:
			if request["price"] > 0: used_resource += request["price"]
		efficiency = used_resource * 1.0 / total_resource
		# Calculate fairness
		if self.power_type == 1:
			rejected_normal = len([1 for c in self.request_records if c["price"] == -1])
			rejected_abnormal = len([1 for c in self.request_records if c["price"] == -2])
			fairness = rejected_normal * 1.0 / max(rejected_normal + rejected_abnormal, 1)
		else:
			price_ratio = [c["price"] * 1.0 / c["original_price"] for c in self.request_records if c["price"] > 0]
			fairness = np.mean(price_ratio) / (1 + np.std(price_ratio))
		return efficiency, fairness