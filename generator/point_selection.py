from .algorithms import sdc
import random
import numpy as np

def get_non_air(map_data, np_array=True):
	non_air = np.empty((0,2), int) if np_array else []

	for c in range(map_data.n_cols):
		for r in range(map_data.n_rows):
			if map_data.get(r, c) != "-":
				if np_array:
					non_air = np.append(non_air, np.array([[r,c]]), axis=0)
				else:
					non_air.append((r,c))
	return non_air

def evenly_spaced_selection(map_data, N=3):
	selected_points = []

	solids = get_non_air(map_data, np_array=True)
	mask = sdc.select(solids,
	                  image_shape=(map_data.n_rows, map_data.n_cols),
	                  count=N)

	for i in range(len(mask)):
		if mask[i]:
			r, c = solids[i]
			selected_points.append([r,c])

	return selected_points

def spaced_selection(map_data, N=3, D=3):
	r = random.randint(0, map_data.n_rows)
	c = random.randint(0, map_data.n_cols)

	# store tiles r, c indexes, and probabilities for each
	pop =  get_non_air(map_data, np_array=False)
	pop_d = []

	for i in range(len(pop)):
		pop_d.append(1/len(pop))

	def update_chances(pop, pop_d, r, c, D):
		if D < 0: return

		# update probabilities of all 4 neighbours
		update_chances(pop, pop_d, r+1, c, D-1)
		update_chances(pop, pop_d, r, c+1, D-1)
		update_chances(pop, pop_d, r-1, c, D-1)
		update_chances(pop, pop_d, r, c-1, D-1)

		for i in reversed(range(len(pop))):
			if pop[i] == (r, c):
				#print("Removing {},{} from list".format(r,c))
				pop_d.remove(pop_d[i])
				pop.remove(pop[i])

	selected_points = []
	import numpy as np
	while len(selected_points) < N and len(pop_d) > 0:
		index = np.random.choice(len(pop_d), 1, p=pop_d)[0]
		r, c = pop[index]
		#print("Updating R, C {},{}".format(r,c))
		update_chances(pop, pop_d, r, c, D)
		for i in range(len(pop)):
			pop_d[i] = 1/len(pop)
		selected_points.append((r,c))

	# assert statement to check if points indeed D distance apart
	def get_manhattan(p1,p2):
		return abs(p1[0]-p2[0])+abs(p1[1]-p2[1])

	for i in range(len(selected_points)-1):
		for j in range(i+1, len(selected_points)):
			p1 = selected_points[i]
			p2 = selected_points[j]
			#print("Distance between {} and {}: {}".format(p1, p2, get_manhattan(p1, p2)))
			assert (get_manhattan(p1, p2)>D), "Distance between points > D!"

	return selected_points
