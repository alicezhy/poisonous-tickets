# This is the most basical counselor for power type 1, which will always say yes
# It takes four arguments - a class representing the railway system, and a most recent request to decide on: (train, idx_start, idx_end). Notice that the index is based on the specific train rather than the global label of stations.
# Counselors of power type 1 are *NOT* supposed to modify the railway_system
def counselor(railway_system, train, idx_start, idx_end):
	return True
