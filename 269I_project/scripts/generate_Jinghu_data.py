# Run this script to generate all the info related to trains on Jinghu-railway

import json
import numpy as np

station_metadata = [
	["北京南", 0, 2173],
	["廊坊", 59, 474],
	["天津南", 131, 1562],
	["沧州西", 219, 755],
	["德州东", 327, 579],
	["济南西", 419, 723],
	["泰安", 462, 563],
	["曲阜东", 533, 65],
	["滕州东", 589, 171],
	["枣庄", 625, 391],
	["徐州东", 688, 876],
	["宿州东", 767, 565],
	["蚌埠南", 844, 381],
	["定远", 897, 80],
	["滁州", 959, 454],
	["南京南", 1018, 833],
	["镇江南", 1087, 318],
	["丹阳北", 1112, 97],
	["常州北", 1144, 471],
	["无锡东", 1201, 655],
	["苏州北", 1227, 1068],
	["昆山南", 1259, 165],
	["上海虹桥", 1302, 2420]
]
stations_info = {}
station_to_new_idx = {}
for i, tpl in enumerate(station_metadata):
	stations_info[i] = {"name" : tpl[0], "position" : tpl[1], "population" : tpl[2]}
	station_to_new_idx[tpl[0]] = i

# Load train list
with open("../../generate_railroad_map/train_to_line_map.json", "r") as f:
	train_to_line_map = json.load(f)
with open("../../generate_railroad_map/station_to_index_map.json", "r") as f:
	station_to_index_map = json.load(f)
index_to_station_map = {}
for station in station_to_index_map:
	index_to_station_map[station_to_index_map[station]] = station

with open("../Jinghu-All/stations_info.json", "w") as f:
	json.dump(stations_info, f)
for train in train_to_line_map:
	line = train_to_line_map[train]
	c1 = index_to_station_map[line[0][0]]
	c2 = index_to_station_map[line[-1][0]]
	if (c1 == "北京南") and (c2 == "上海虹桥"):
		num_stop = len(line)
		train_info = np.zeros((num_stop, 3))
		for i in range(num_stop):
			train_info[i, 0] = station_to_new_idx[index_to_station_map[line[i][0]]]
		for i in range(num_stop - 1):
			train_info[i, 1] = stations_info[train_info[i + 1, 0]]["position"] - stations_info[train_info[i, 0]]["position"]
		train_info = train_info.astype(int)
		print (train, train_info)
		np.save("../Jinghu-All/" + train, train_info)


		