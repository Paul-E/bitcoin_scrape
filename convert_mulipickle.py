from argparse import ArgumentParser
from pickle import load, dump

parser = ArgumentParser("Convert pickle file with many independent objects in to pickle file with list of those objects.")
parser.add_argument("input_file")
parser.add_argument("output_file")
args = parser.parse_args()

pickled_objects = []
with open(args.input_file, "rb") as pickle_file:
    while True:
        try:
            pickled_objects.append(load(pickle_file))
        except EOFError:
            break

with open(args.output_file, "wb") as output_pickle:
    dump(pickled_objects, output_pickle)
            
