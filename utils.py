import os
import json
import snap
import matplotlib.pyplot as plt
import numpy as np
import pickle
import random
import copy
from Queue import Queue
from collections import defaultdict

def load_stations_and_trains_and_gps_json(file_dir):
	with open(os.path.join(file_dir, "station_to_index_map.json"), "r") as f:
		station_to_index_map = json.load(f)
	with open(os.path.join(file_dir, "train_to_line_map.json"), "r") as f:
		train_to_line_map = json.load(f)
	with open(os.path.join(file_dir, "station_to_gps_map.json"), "r") as f:
		station_to_gps_map = json.load(f)
	return station_to_index_map, train_to_line_map, station_to_gps_map

def load_map(railroad_map_path):
	weight = {} # weight of edges in the railroad graph
	with open(railroad_map_path, "r") as f:
		header = True
		for line in f: 
			if header:
				header = False
				N, M = map(int, line.split())
				G = snap.TUNGraph().New()
				for i in range(1, N + 1):
					G.AddNode(i)
			else:
				u, v, w = map(int, line.split())
				G.AddEdge(u, v)
				weight[(u, v)] = w
				weight[(v, u)] = w
	return G, N, M, weight

def get_edge_set(G):
	edge_set = set()
	for u_ in G.Nodes():
		u = u_.GetId()
		k = u_.GetDeg()
		for _ in range(k):
			v = u_.GetNbrNId(_)
			if u > v: continue # Only consider edges (u, v) where u < v
			edge_set.add((u, v))
	return edge_set

def get_train_importance(train_to_line_map):
	train_importance = {}
	for train in train_to_line_map:
		c = sum(e[1] for e in train_to_line_map[train] if e[1] is not None)
		if train[0] == "G": 
			c *= 5
		elif train[0] == "D":
			c *= 3
		elif train[0] == "Z":
			c *= 2
		elif train[0] == "T" or train[0] == "C":
			c *= 1.5
		train_importance[train] = c
	return train_importance

# Helper function for many of the algorithms - given a set of edge destroyed, evaluate the total influence
def edge_set_importance(railroad_effect, edge_set, train_importance):
	total_set = set()
	for edge in edge_set:
		total_set = total_set.union(railroad_effect[edge])
	result = 0
	for train in total_set:
		result += train_importance[train]
	return result

def equal_edge(e1, e2):
	u1 = e1[0]; v1 = e1[1]; u2 = e2[0]; v2 = e2[1]
	if u1 > v1: u1, v1 = v1, u1
	if u2 > v2: u2, v2 = v2, u2
	if (u1 == u2) and (v1 == v2): return True
	return False

def find_non_equivalent_neighbor_edge(G, weight, u, v, previous_direction):
	current_edge = (u, v)
	last_edge = current_edge
	while True:
		cnt = 0
		while True:
			next_edge = find_neighbor_edge(G, current_edge[0], current_edge[1])
			if not equal_edge(next_edge, last_edge): 
				if not equal_edge(next_edge, previous_direction):
					last_edge = current_edge
					current_edge = next_edge
					break
			cnt += 1
			if cnt == 100:
				# No other edges
				current_edge = random.sample(weight, 1)[0]
		if weight[current_edge] != weight[(u, v)]: break
	return current_edge

def find_neighbor_edge(G, u, v):
	if random.randint(0, 1) == 0: u, v = v, u
	u_ = G.GetNI(u)
	for i in np.random.permutation(u_.GetDeg()):
		if u_.GetNbrNId(i) != v:
			return u, u_.GetNbrNId(i)
	v_ = G.GetNI(v)
	for i in np.random.permutation(v_.GetDeg()):
		if v_.GetNbrNId(i) != u:
			return v, v_.GetNbrNId(i)
	