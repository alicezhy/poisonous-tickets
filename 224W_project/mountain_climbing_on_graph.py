# This file runs in python 2
# It implements the influence_maximization algorithm based on data file railroad_effect.bin
# Besides that, it has no dependency on external files

import sys
sys.path.append("../")
from utils import *
from multiprocessing import Pool

railroad_map_path = "../generate_railroad_map/railroad_map.txt"
stations_json_path = "../generate_railroad_map/"

G, N, M, weight = load_map(railroad_map_path)
with open("railroad_effect.bin", "r") as f:
	railroad_effect = pickle.load(f)
station_to_index_map, train_to_line_map, station_to_gps_map = load_stations_and_trains_and_gps_json(stations_json_path)
train_importance = get_train_importance(train_to_line_map) # support custom train importance
index_to_station_map = {}
for station in station_to_index_map:
	c = station_to_index_map[station]
	index_to_station_map[c] = station

K = 100
current_set = set()
result = []
railroad_selected = []
for c in range(K):
	max_railroad = None
	max_increase = 0
	for railroad in railroad_effect:
		st = sum([train_importance[train] for train in (railroad_effect[railroad] - current_set)])
		if st > max_increase:
			max_increase = st
			max_railroad = railroad
	railroad_selected.append(max_railroad)
	current_set = current_set.union(railroad_effect[max_railroad])
	current_influence = sum([train_importance[train] for train in current_set])
	#print "Include a new railroad:", index_to_station_map[max_railroad[0]], index_to_station_map[max_railroad[1]]
	#print "Railroad destroyed: %d, trains affected: %d" % (c + 1, current_influence)
	result.append(current_influence)

# Conduct local mountain-climbing on the railroad set, based on the graph
def optimize_set_for_K(initial_set, initial_influence, G, weight, railroad_effect, train_importance, K):
	best_influence = initial_influence
	thresh = 0.01
	for __ in range(1000):
		current_set = copy.deepcopy(initial_set)
		last_edge = copy.deepcopy(initial_set)
		current_influence = initial_influence
		for _ in range(50000):
			c = random.randint(0, K - 1)
			u, v = find_non_equivalent_neighbor_edge(G, weight, current_set[c][0], current_set[c][1], last_edge[c])
			tmp_set = current_set[:c] + [(u, v)] + current_set[c + 1:]
			tmp_influence = edge_set_importance(railroad_effect, tmp_set, train_importance)
			if tmp_influence > best_influence:
				best_influence = tmp_influence
				current_influence = tmp_influence
				current_set = tmp_set
				last_edge[c] = (u, v)
				#print "New best result found for K = %d: %d" % (K, best_influence)
				print K, best_influence
			else:
				if random.uniform(0, 1) < 0.5 * np.exp(thresh * (tmp_influence - current_influence)):
					current_influence = tmp_influence
					current_set = tmp_set
					last_edge[c] = (u, v)
			#if _ % 1 == 0:
			#	print "Step %d: current influence is %d." % (_, current_influence)
def optimize_set_for_K_wrapper(k):
	optimize_set_for_K(railroad_selected[:k], result[k - 1], G, weight, railroad_effect, train_importance, k)

p = Pool(100)
p.map(optimize_set_for_K_wrapper, range(1, 101))
#optimize_set_for_K_wrapper(100)

# plt.clf()
# plt.title("(Maximum) Total importance of trains affected as railroads destroyed")
# plt.xlabel("# of railroads destroyed")
# plt.ylabel("# of trains affected")
# plt.plot(range(1, K + 1), result)
# plt.savefig("influence_maximization")
# plt.show()