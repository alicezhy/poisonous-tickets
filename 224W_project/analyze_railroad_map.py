# This code is in Python 2 since it uses SNAP
# Analyze the basic structure of the map

import sys
sys.path.append("../")
from utils import *
import snap
import matplotlib.pyplot as plt
import numpy as np
import pickle
from Queue import Queue
from collections import defaultdict

railroad_map_path = "../generate_railroad_map/railroad_map.txt"
stations_json_path = "../generate_railroad_map/"

# Notice - all the nodes (stations) in this project is 1-indexed
G, N, M, weight = load_map(railroad_map_path)
station_to_index_map, train_to_line_map, station_to_gps_map = load_stations_and_trains_and_gps_json(stations_json_path)
index_to_station_map = {}
for station in station_to_index_map:
	c = station_to_index_map[station]
	index_to_station_map[c] = station

# Node degree distribution
def check_degree_distribution(G, station_to_index_map):
	station_degree_pairs = []
	for c in station_to_index_map:
		idx = station_to_index_map[c]
		v = G.GetNI(idx)
		station_degree_pairs.append((v.GetDeg(), c))
	station_degree_pairs.sort(reverse=True)
	for i in range(20):
		print station_degree_pairs[i][1], station_degree_pairs[i][0]
	degs = [c[0] for c in station_degree_pairs]
	plt.clf()
	plt.title("Degree distribution of all stations")
	plt.xlabel("degree")
	plt.ylabel("# of stations")
	plt.hist(degs, bins=11)
	plt.savefig("degree_distribution")
	plt.show()
#check_degree_distribution(G, station_to_index_map)

# Calculate the pairwise shortest distance; return a matrix of distance
# Since this behavior could be time-consuming, we will store the result and reload it later
# Notice that weight could be anything - distance, importance, some constant, etc. The corresponding save_file_name should be different
def pairwise_shortest_distance(G, N, M, weight, save_file_name=None, allow_cache=True):
	if allow_cache:
		try:
			dist = np.load(save_file_name)
			return dist
		except:
			pass
	dist = np.full((N + 1, N + 1), np.inf)
	for i in range(1, N + 1): 
		print i
		dist[i, i] = 0
		u = Queue()
		u.put(i)
		while not u.empty():
			cs = u.get() # Update through edge (cs, ct)
			v = G.GetNI(cs)
			k = v.GetDeg()
			for j in range(k):
				ct = v.GetNbrNId(j)
				if dist[i, cs] + weight[(cs, ct)] < dist[i, ct]:
					dist[i, ct] = dist[i, cs] + weight[(cs, ct)]
					u.put(ct)
	np.save(save_file_name, dist)
	return dist

dist = pairwise_shortest_distance(G, N, M, weight, "station_pairwise_shortest_distance.npy")

# For each primitive railroad block, calculate the set of trains that will be affected due to the break of this block
# Notice that sometimes a railroad is a sub-interval of two consecutive stops. In that case, (u, v) contains block (x, y) iff dist(u, x) + dist(x, y) + dist(y, v) = dist(u, v), or dist(u, y) + dist(y, x) + dist(x, v) = dist(u, v)
# Return a dict of dict. e.g. {(3, 5) : {"G1" : True, "G17" : True}}

def calculate_railroad_effect(G, train_to_line_map, allow_cache=True):
	save_file_name = "railroad_effect.bin"
	if allow_cache:
		try:
			with open(save_file_name, "r") as f:
				railroad_effect = pickle.load(f)
			return railroad_effect
		except:
			pass
	railroad_effect = defaultdict(set)
	cnt = 0
	processed_edges = 0
	for edge in get_edge_set(G):
		u = edge[0]
		v = edge[1]
		processed_edges += 1
		per_road_count = 0
		for train in train_to_line_map:
			flag = False
			stops = train_to_line_map[train]
			num_stops = len(stops)
			for i in range(num_stops - 1):
				tu = stops[i][0]
				tv = stops[i + 1][0]
				if np.isinf(dist[tu, u]) or np.isinf(dist[tu, v]) or np.isinf(dist[u, tv]) or np.isinf(dist[v, tv]):
					continue
				if dist[tu, u] + dist[u, v] + dist[v, tv] == dist[tu, tv]:
					#print index_to_station_map[tu], index_to_station_map[tv], "  contains  ", index_to_station_map[u], index_to_station_map[v], stops[i][1], train
					flag = True
					break
				if dist[tu, v] + dist[v, u] + dist[u, tv] == dist[tu, tv]:
					flag = True
					break
			if flag:
				cnt += 1
				per_road_count += 1
				railroad_effect[(u, v)].add(train)
		print processed_edges, index_to_station_map[u], index_to_station_map[v], per_road_count
	print cnt
	with open(save_file_name, "w") as f:
		pickle.dump(railroad_effect, f)
	return railroad_effect
railroad_effect = calculate_railroad_effect(G, train_to_line_map)


# Recalculate the distance with weight equal to its importance
importance = {}
for railroad in railroad_effect:
	c = len(railroad_effect[railroad])
	importance[railroad] = 1000 - c
	importance[(railroad[1], railroad[0])] = 1000 - c
dist = pairwise_shortest_distance(G, N, M, importance, "station_pairwise_shortest_distance_importance.npy")
