from pathfinding import find_shortest_path
from graph import Graph


class Drone:
    def __init__(self, id, graph, start, end):
        self.id = id
        self.zone = start
        self.index = 0
        self.path = find_shortest_path(graph, start, end)

    
    def move(self):
        if self.index == len(self.path) - 1:
            return
        self.index += 1
        self.zone = self.path[self.index]
