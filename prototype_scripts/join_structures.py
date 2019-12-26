import os
if __name__ == '__main__': 

    path = "/Users/eduardohauck/Research/MarioAI/MarioAI_PCG/graphs/"
    files = [f for f in os.listdir(path)]

    inputs = []

    for f in files:
        #ignore other files
        print(f)
        input_file = open(path+f, "r")

        inputs.append(input_file)

    index = 0
    for i in inputs:

    	for l in i:
    	 print(l)
