# This file runs in python 2
# It implements the influence_maximization algorithm based on data file railroad_effect.bin
# Besides that, it has no dependency on external files

import sys
sys.path.append("../")
from utils import *

railroad_map_path = "../generate_railroad_map/railroad_map.txt"
stations_json_path = "../generate_railroad_map/"

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
for c in range(K):
	max_railroad = None
	max_increase = 0
	for railroad in railroad_effect:
		st = sum([train_importance[train] for train in (railroad_effect[railroad] - current_set)])
		if st > max_increase:
			max_increase = st
			max_railroad = railroad
	current_set = current_set.union(railroad_effect[max_railroad])
	current_influence = sum([train_importance[train] for train in current_set])
	print "Include a new railroad:", index_to_station_map[max_railroad[0]], index_to_station_map[max_railroad[1]]
	print "Railroad destroyed: %d, trains affected: %d" % (c + 1, current_influence)
	result.append(current_influence)

print (result)
plt.clf()
plt.title("Total influence as railroads destroyed")
plt.xlabel("# of railroads destroyed")
plt.ylabel("# of trains affected")
plt.plot(range(1, K + 1), result)
plt.savefig("influence_maximization")
plt.show()