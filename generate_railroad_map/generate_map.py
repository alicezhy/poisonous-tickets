# This code is in Python 3
import sys
sys.path.append("../")
from utils import *

station_to_index_map, train_to_line_map, station_to_gps_map = load_stations_and_trains_and_gps_json(".")
index_to_station_map = {}
for station in station_to_index_map:
	c = station_to_index_map[station]
	index_to_station_map[c] = station

def get_Chinese_name(x):
	return index_to_station_map[x]

not_an_edge = set()
# List edges that are not primitive railroads
for train in train_to_line_map:
	stops = train_to_line_map[train]
	num_stops = len(stops)
	for i in range(num_stops):
		for j in range(i + 2, num_stops):
			not_an_edge.add((stops[i][0], stops[j][0]))
# Add the rest of them
edges = set()
for train in train_to_line_map:
	stops = train_to_line_map[train]
	num_stops = len(stops)
	for i in range(num_stops - 1):
		x = stops[i][0]
		y = stops[i + 1][0]
		if not (x, y) in not_an_edge:
			xname = get_Chinese_name(x)
			yname = get_Chinese_name(y)
			edges.add((x, y))

for edge in edges:
	print (get_Chinese_name(edge[0]), get_Chinese_name(edge[1]))
