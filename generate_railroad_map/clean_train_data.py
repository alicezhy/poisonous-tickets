# This code is in Python 3
import os
import datetime
import time
import json

import sys
sys.path.append("../")
from utils import *

def diff_minutes(str1, str2):
	h1, m1 = map(int, str1.split(":"))
	h2, m2 = map(int, str2.split(":"))
	c = (h2 - h1) * 60 + (m2 - m1)
	if c < 0: c += 24 * 60
	return c
	
# Load all data
all_files = os.listdir("../raw_data/raw_train_data/")
#all_files = ["T66.txt", "1230.txt"]
all_stations = {}
cnt_stations = 0
all_data = {}
for i, file in enumerate(all_files):
	#print ("Processing train %s: %d / %d" % (file, i + 1, len(all_files)))
	with open("../raw_data/raw_train_data/%s" % file, "r") as f:
		count = 0
		data = []
		for line in f:
			count += 1
			if count >= 26:
				cc = line.split("|")
				try:
					# Station name
					l = cc[1].find("[")
					r = cc[1].find("]")
					station_name = cc[1][l + 1 : r]
					if ":" in station_name: continue
					if not (station_name in all_stations):
						cnt_stations += 1
						all_stations[station_name] = cnt_stations
					station_name = all_stations[station_name]
					# arrive / leave time
					arrive_time = str.lstrip(str.rstrip(cc[2]))
					leave_time = str.lstrip(str.rstrip(cc[3]))
					if len(leave_time) != 5:
						leave_time = arrive_time
					data.append([station_name, arrive_time, leave_time])
				except IndexError:
					# We're done extracting all stations
					break
		for i in range(len(data) - 1):
			data[i][1] = diff_minutes(data[i][2], data[i + 1][1])
			data[i] = data[i][:2]
		data[-1] = [data[-1][0], None]
		all_data[file.split(".")[0]] = data

with open("station_to_index_map.json", "w") as f:
	json.dump(all_stations, f)

with open("train_to_line_map.json", "w") as f:
	json.dump(all_data, f)
