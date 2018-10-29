import os
import json

def load_stations_and_trains_and_gps_json(file_dir):
	with open(os.path.join(file_dir, "station_to_index_map.json"), "r") as f:
		station_to_index_map = json.load(f)
	with open(os.path.join(file_dir, "train_to_line_map.json"), "r") as f:
		train_to_line_map = json.load(f)
	with open(os.path.join(file_dir, "station_to_gps_map.json"), "r") as f:
		station_to_gps_map = json.load(f)
	return station_to_index_map, train_to_line_map, station_to_gps_map
