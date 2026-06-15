import sys
from simulation import simulate
from graph import Graph
from parsing import DroneMap, parsing
from pathfinding import find_two_shortest_paths
# from visualisation import Visualizer


if __name__ == "__main__":
    drone_map = DroneMap()
    try:
        parsing(drone_map)
    except ValueError as e:
        print(e)
        sys.exit(1)

    graph = Graph()

    for zone in drone_map.zones.values():
        graph.add_zone(zone)

    for conn in drone_map.connections:
        graph.add_connection(conn)

    # visual = Visualizer(drone_map)
    history = simulate(drone_map, graph)
    # visual.visualisation(drone_map, history)

    start = drone_map.start
    end = drone_map.end

    paths = find_two_shortest_paths(graph, start, end)
    print(f"Found {len(paths)} paths:")
    for p in paths:
        print(p)
