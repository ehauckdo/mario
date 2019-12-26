import os, sys
import statistics

# count the number of connecting nodes in each structure
def read_substructure_stats(filename):
    input_file = open(filename, "r")

    stats = {}
    for i in range(5):
        stats[i] = 0

    for line in input_file:
        s_id, connecting, combinable = line.split(",")
        stats[int(connecting)] += 1
        
    print("{ID: num_connecting_nodes}")
    print(stats)
    input_file.close()

# count the number of structures used in each map
def read_map_stats(filename):
    input_file = open(filename, "r")

    num_structures = 0

    for line in input_file:
        s_id, count = line.split(":")
        num_structures += int(count)

    input_file.close()
    return num_structures

if __name__ == '__main__': 

    path = "/Users/eduardohauck/Research/MarioAI/MarioAI_PCG"#os.path.dirname(sys.argv[0])
    files = [f for f in os.listdir(path)]
    structures_per_map = []

    # # Parse the files into a dictionary
    for f in files:
        #ignore other files
        if "stats.txt" not in f or "subs" in f: continue
        print(f)
        structures_per_map.append(read_map_stats(f))

    print(sorted(structures_per_map))
    print(sum(structures_per_map)/len(structures_per_map))
    mininum = min(structures_per_map)
    maximum = max(structures_per_map)
    avg = sum(structures_per_map)/len(structures_per_map)
    std = statistics.stdev(structures_per_map)
    print("Min: {}, Max: {}, Avg: {}, STD: {}".format(mininum, maximum, avg, std))

    read_substructure_stats("output_substructures_stats.txt")