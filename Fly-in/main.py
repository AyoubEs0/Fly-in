import sys
from simulation import DroneSimulator
from graph import Graph
from parsing import DroneMap, parsing
from pathfinding import PathFinder
from visualisation import Visualizer


if __name__ == "__main__":
    try:
        drone_map = DroneMap()
        parsing(drone_map)

        graph = Graph()

        for zone in drone_map.zones.values():
            graph.add_zone(zone)

        for conn in drone_map.connections:
            graph.add_connection(conn)

        visual = Visualizer(drone_map)
        simulator = DroneSimulator(drone_map, graph)
        history = simulator.simulate()
        visual.visualisation(drone_map, history)

        start = drone_map.start
        end = drone_map.end

        if start is None or end is None:
            sys.exit(1)

        path_finder = PathFinder(graph)

        paths = path_finder.find_two_shortest_paths(start, end)

    except ValueError as e:
        print(e)
        sys.exit(1)

    except FileNotFoundError as e:
        print(e)

    except KeyboardInterrupt:
        print("\nProgram stopped by the user")

    except Exception as e:
        print(e)
