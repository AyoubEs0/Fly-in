import sys
from drone import Drone
from graph import Graph
from parsing import read_file, parse 


lines = read_file(sys.argv[1])
map_dict = parse(lines)

def simulate(map_dict, graph):
