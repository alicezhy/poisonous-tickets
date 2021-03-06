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
			x = stops[i][0]
			y = stops[j][0]
			if x > y: x, y = y, x
			not_an_edge.add((x, y))
# Add the rest of them
edges = {} # map edge to weight (minimum time to pass)
for train in train_to_line_map:
	stops = train_to_line_map[train]
	num_stops = len(stops)
	for i in range(num_stops - 1):
		x = stops[i][0]
		y = stops[i + 1][0]
		w = stops[i][1]
		if x > y: x, y = y, x
		if not (x, y) in not_an_edge:
			if not (x, y) in edges:
				edges[(x, y)] = w
			elif w < edges[(x, y)]:
				edges[(x, y)] = w

for edge in edges:
	print (get_Chinese_name(edge[0]), get_Chinese_name(edge[1]), edges[edge], edge[0], edge[1])

# The format of railroad_map: 
# 	First line: N (number of stations), M (number of primitive railroads)
#	Following M lines, three integers (x, y, z), indicating an edge and the minimum passing time
with open("railroad_map.txt", "w") as f:
	f.write("%d %d\n" % (len(station_to_index_map), len(edges)))
	for edge in edges:
		f.write("%d %d %d\n" % (edge[0], edge[1], edges[edge]))






