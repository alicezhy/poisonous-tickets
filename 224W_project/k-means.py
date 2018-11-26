# This file runs in python 2
# It implements the k-means algorithm based on data file railroad_effect.bin and the pairwise distance between stations

import sys
sys.path.append("../")
from utils import *

pairwise_distance_metric = "importance" # It could be "distance" or "unit" or "importance"
railroad_map_path = "../generate_railroad_map/railroad_map.txt"
stations_json_path = "../generate_railroad_map/"

def K_means(N, dist, K):
	not_connected_nodes = set()
	for i in range(1, N + 1):
		if np.isinf(dist[i, 1]): # check connectivity with Guangzhou Dong
			not_connected_nodes.add(i)
	K_centers = None
	while True:
		K_centers = [random.randint(1, N) for i in range(K)]
		if len(set(K_centers) - not_connected_nodes) == K: break # All centers should be distinct
	assign = np.full((N + 1), -1)
	for _ in range(100):
		last_K_centers = copy.deepcopy(K_centers)
		for i in range(1, N + 1):
			if i in not_connected_nodes: continue
			min_dist = dist[i, K_centers[0]]
			closest_center = 0
			for j in range(1, K):
				if dist[i, K_centers[j]] < min_dist:
					min_dist = dist[i, K_centers[j]]
					closest_center = j
			assign[i] = closest_center
		for i in range(K):
			nodes = [c for c in range(1, N + 1) if assign[c] == i]
			best_new_center = None
			min_total_distance = float("inf")
			for node in nodes:
				ss = 0
				for pia in nodes:
					ss += dist[pia, node]
				if ss < min_total_distance:
					min_total_distance = ss
					best_new_center = node
			K_centers[i] = best_new_center
		#print " ".join([index_to_station_map[i] for i in K_centers])
		if K_centers == last_K_centers: break
	return K_centers, assign


def maximize_influence_with_K_edges(railroad_effect, G, N, dist, K):
	best_result = set()
	maximum_importance = 0
	for _ in range(10):
		K_centers, assign = K_means(N, dist, (K + 1) / 2)
		# Influence maximization, but each cluster only has one slot; the ordering of the clusters is random, as well
		current_set = set()
		for c in range(K):
			max_railroad = None
			max_increase = -1
			for railroad in railroad_effect:
				if c < (K + 1) / 2:
					if (assign[railroad[0]] != c) or (assign[railroad[1]] != c): continue # must be inside the current cluster
				st = sum([train_importance[train] for train in (railroad_effect[railroad] - current_set)])
				if st > max_increase:
					max_increase = st
					max_railroad = railroad
			if max_railroad is not None:
				current_set = current_set.union(railroad_effect[max_railroad])
		current_importance = sum([train_importance[train] for train in current_set])
		if current_importance > maximum_importance:
			maximum_importance = current_importance
			best_result = current_set
		print "K = %d, Round %d: current best result is %d." % (K, _ + 1, maximum_importance)
	return maximum_importance


if __name__ == "__main__":
	if pairwise_distance_metric == "distance":
		pairwise_distance_file = "station_pairwise_shortest_distance.npy"
	elif pairwise_distance_metric == "unit":
		pairwise_distance_file = "station_pairwise_shortest_distance_unit.npy"
	elif pairwise_distance_metric == "importance":
		pairwise_distance_file = "station_pairwise_shortest_distance_importance.npy"

	G, N, M, weight = load_map(railroad_map_path)
	station_to_index_map, train_to_line_map, station_to_gps_map = load_stations_and_trains_and_gps_json(stations_json_path)
	index_to_station_map = {}
	train_importance = get_train_importance(train_to_line_map) # support custom train importance
	for station in station_to_index_map:
		c = station_to_index_map[station]
		index_to_station_map[c] = station
	dist = np.load(pairwise_distance_file)

	with open("railroad_effect.bin", "r") as f:
		railroad_effect = pickle.load(f)

	#print len(maximize_influence_with_K_edges(railroad_effect, G, N, dist, K = 14))
	# ah = K_means(N, dist, 7)
	# for i in ah:
	# 	print index_to_station_map[i]
	result = []
	for K in range(1, 101):
		result.append(maximize_influence_with_K_edges(railroad_effect, G, N, dist, K))
		print "K = %d, influence = %d" % (K, result[-1])
	print result