from .substructure import Substructure, Node

def instantiate_base_level(id_substructures):
	g_s = Substructure(id_substructures)

	for c in range(3):
		platform = Node(15, c, "X")
		platform.type = "Solid"
		platform.cluster_id = g_s.id
		g_s.insert_node(platform)

	mario = Node(14, 1, "M")
	mario.cluster_id = g_s.id
	g_s.insert_node(mario)

	connecting = Node(15, 3, "*", g_s.id, 0, 0, "Connecting")
	connecting.add_edge(connecting, {"direction":"r", "combinable":[]})
	g_s.insert_node(connecting)

	id_substructures += 1

	g_f = Substructure(id_substructures)

	for c  in range(2,4):
		platform = Node(11, c, "X")
		platform.type = "Solid"
		platform.cluster_id = g_f.id
		g_f.insert_node(platform)

	finish = Node(10, 2, "F")
	finish.cluster_id = g_f.id
	g_f.insert_node(finish)

	connecting = Node(15, 0, "*", g_f.id, 0, 0, "Connecting")
	connecting.id =  g_f.id
	connecting.add_edge(connecting, {"direction":"l", "combinable":[]})
	g_f.insert_node(connecting)

	return g_s, g_f
