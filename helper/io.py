import pickle

# Save a certain Python object to disk
# using the pickle library
def save(object, filename):
    with open(filename, 'wb') as output_file:
        pickle.dump(object, output_file)

# Load a certain Python object to disk
# using the pickle library
def load(filename):
    with open(filename, 'rb') as input_file:
        object = pickle.load(input_file)
        return object
