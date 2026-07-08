import sys
from drone import Drone
from pathfinding import PathFinder
from parsing import DroneMap
from graph import Graph
from typing import Dict, List, Tuple
import heapq


class DroneSimulator:
    """Simulates drones moving through the graph."""
    def __init__(self, drone_map: DroneMap, graph: Graph):
        """
        Initializes the drone simulator.

        Args:
        drone_map (DroneMap): Parsed map data.
        graph (Graph): Graph of zones and connections.
        """
        self.drone_map = drone_map
        self.graph = graph

    def initialize_conn_capacity(
            self, paths: List[Tuple[float, List[str]]]) -> Dict[
                Tuple[str, str], int]:
        conn_capacity = {}

        for _, path in paths:
            for i in range(len(path) - 1):
                key = (path[i], path[i + 1])
                conn_capacity[key] = 0

        return conn_capacity

    def simulate(self) -> List[Dict[int, str]]:
        """
        Simulates drone movement until all drones reach the destination.

        Returns:
        List[Dict[int, str]]: History of drone positions at each turn.
        """
        i = 1
        drones = []

        start = self.drone_map.start
        end = self.drone_map.end

        if start is None or end is None:
            sys.exit(1)

        path_finder = PathFinder(self.graph)

        paths = path_finder.find_two_shortest_paths(start, end)

        if not paths:
            raise ValueError("No path found")

        heapq.heapify(paths)
        while i < self.drone_map.nb_drones + 1:
            cost, path = heapq.heappop(paths)
            drones.append(Drone(i, self.graph, start, end, path))
            cost += cost // 2
            heapq.heappush(paths, (cost, path))
            i += 1

        drones_zones = {zone_name: 0 for zone_name in self.drone_map.zones}
        drones_zones[start] = self.drone_map.nb_drones

        drones_positions = {drone.id: start for drone in drones}

        history = []
        history.append(dict(drones_positions))

        turns = 1

        in_transit_counter = 0
        while (
            drones_zones[end] != self.drone_map.nb_drones
            or in_transit_counter > 0
        ):

            print(f"Turn {turns}: ", end="")

            turn_conn_usage = self.initialize_conn_capacity(paths)

            for drone in drones:

                if drone.in_transit:
                    dest = drone.transit_destination
                    drone.in_transit = False
                    in_transit_counter -= 1
                    drone.move()

                    print(f"D{drone.id}-{dest}", end=" ")

                    drone.transit_destination = ""
                    drones_positions[drone.id] = drone.zone

                    continue

                if drone.zone == end:
                    continue

                next_zone = drone.path[drone.index + 1]

                max_capacity = 1
                for link in self.graph.connections[drone.zone]:
                    if link.neighbor == next_zone:
                        max_capacity = link.max_link_capacity
                        break

                key = (drone.zone, next_zone)

                if self.drone_map.zones[next_zone].zone == "restricted":
                    if (
                        drones_zones[next_zone] < self.drone_map.zones[
                            next_zone].max_drones
                        and turn_conn_usage[key] < max_capacity
                    ):
                        turn_conn_usage[key] += 1

                        old = drone.zone
                        drone.in_transit = True
                        in_transit_counter += 1
                        drone.transit_destination = next_zone

                        drones_zones[old] -= 1
                        drones_zones[next_zone] += 1

                        print(f"D{drone.id}-({old}-{next_zone})", end=" ")
                        drones_positions[drone.id] = f"{old}-{next_zone}"

                    continue

                if (
                    drones_zones[next_zone] < self.drone_map.zones[
                        next_zone].max_drones
                    and turn_conn_usage[key] < max_capacity
                ):

                    turn_conn_usage[key] += 1

                    old = drone.zone
                    drone.move()

                    drones_zones[old] -= 1
                    drones_zones[drone.zone] += 1

                    print(f"D{drone.id}-{drone.zone}", end=" ")
                    drones_positions[drone.id] = drone.zone

                continue

            history.append(dict(drones_positions))

            print()
            turns += 1

        return history
