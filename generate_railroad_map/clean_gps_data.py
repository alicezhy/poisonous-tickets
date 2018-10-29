import sys
sys.path.append("../")
from utils import *

station_to_gps_map = {}
with open("../raw_data/station_to_gps_raw.txt", "r") as f:
	for line in f:
		data = line.rstrip().split("\t")
		station_to_gps_map[data[0]] = (data[-1], data[-2])
		if (data[0][-1] == u"站"):
			station_to_gps_map[data[0][:-1]] = (data[-1], data[-2])
with open("../raw_data/station_to_gps_raw_more.txt", "r") as f:
	for line in f:
		data = line.rstrip().split("\t")
		assert (data[0][-3:] == u"火车站")
		data[0] = data[0][:-3]
		station_to_gps_map[data[0]] = (data[-2], data[-1])
		
with open("./station_to_gps_map.json", "w") as f:
	json.dump(station_to_gps_map, f)