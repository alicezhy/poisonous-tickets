# This file runs in python 2
# It implements the influence_maximization algorithm based on data file railroad_effect.bin
# Besides that, it has no dependency on external files

import sys
sys.path.append("../")
from utils import *
from collections import defaultdict

railroad_map_path = "../generate_railroad_map/railroad_map.txt"
stations_json_path = "../generate_railroad_map/"

with open("railroad_effect.bin", "r") as f:
    railroad_effect = pickle.load(f)

station_to_rails = defaultdict(list)
station_neighbors = defaultdict(list)
for s1, s2 in railroad_effect:
    station_to_rails[s1].append((s1, s2))
    station_to_rails[s2].append((s1, s2))
    station_neighbors[s1].append(s2)
    station_neighbors[s2].append(s1)

station_to_index_map, train_to_line_map, station_to_gps_map = load_stations_and_trains_and_gps_json(stations_json_path)
train_importance = get_train_importance(train_to_line_map) # support custom train importance
index_to_station_map = {}
for station in station_to_index_map:
    c = station_to_index_map[station]
    index_to_station_map[c] = station

drop_stations = set()
for s in station_to_rails:
    if len(station_to_rails[s]) != 2: continue
    r1, r2 = station_to_rails[s]
    imp1 = sum([train_importance[train] for train in railroad_effect[r1]])
    imp2 = sum([train_importance[train] for train in railroad_effect[r2]])
    if imp1 == imp2:
        drop_stations.add(s)

def construct_new_rail(s_keep, s_drop):
    if s_drop not in drop_stations: return [s_keep, s_drop]
    nbr1, nbr2 = station_neighbors[s_drop]
    new_drop = nbr1 if nbr1 != s_keep else nbr2
    result = [s_keep]
    result.extend(construct_new_rail(s_drop, new_drop))
    return result

railmap = {}
compressed_effect = {}
for s1, s2 in railroad_effect:
    if s1 in drop_stations: continue
    if s2 in drop_stations:
        new_rail = construct_new_rail(s1, s2)
        key = (new_rail[0], new_rail[-1], new_rail[1])
        if key in compressed_effect:
            print new_rail
            assert(False)
        for i in range(len(new_rail) - 1):
            railmap[(new_rail[i], new_rail[i+1])] = key
        compressed_effect[key] = railroad_effect[(s1, s2)]
    else:
        key = (s1, s2, None)
        railmap[(s1, s2)] = key
        compressed_effect[key] = railroad_effect[(s1, s2)]

with open("compressed_effect.bin", "w") as f:
    pickle.dump(compressed_effect, f)

with open("railmap.bin", "w") as f:
    pickle.dump(railmap, f)