from drone import Drone
from pathfinding import find_two_shortest_paths
from parsing import DroneMap
from graph import Graph
from typing import Dict, List, Union
import heapq


def simulate(
        drone_map: DroneMap,
        graph: Graph) -> List[Dict[int, Union[str, None]]]:
    i = 1
    drones = []

    start = drone_map.start
    end = drone_map.end

    paths = find_two_shortest_paths(graph, start, end)

    heapq.heapify(paths)
    while i < drone_map.nb_drones + 1:
        cost, path = heapq.heappop(paths)
        drones.append(Drone(i, graph, start, end, path))
        cost += cost // 2
        heapq.heappush(paths, (cost, path))
        i += 1

    drones_zones = {zone_name: 0 for zone_name in drone_map.zones.keys()}
    drones_zones[start] = drone_map.nb_drones

    drones_positions = {drone.id: start for drone in drones}

    history = []

    history.append(dict(drones_positions))

    turns = 1
    while drones_zones[end] != drone_map.nb_drones:
        print(f"Turn {turns}: ", end="")

        conn_capacity = {
            (zone1, link.neighbor): 0
            for zone1, links in graph.connections.items()
            for link in links
            }

        for drone in drones:
            if drone.in_transit:
                if (
                    drones_zones[
                        drone.transit_destination
                        ] < drone_map.zones[
                            drone.transit_destination].max_drones):
                    drone.in_transit = False
                    drone.move()
                    print(f"D{drone.id}-{drone.transit_destination}", end=" ")
                    drones_zones[drone.zone] += 1
                    drone.transit_destination = None
                    drones_positions[drone.id] = drone.zone
                    continue

            if drone.zone == end:
                continue

            next_zone = drone.path[drone.index + 1]

            max_capacity: int = 0

            for link in graph.connections[drone.zone]:
                if link.neighbor == next_zone:
                    max_capacity = link.max_link_capacity
                    break

            if next_zone == drone_map.end:
                drones_zones[drone.zone] -= 1
                drone.move()
                print(f"D{drone.id}-{drone.zone}", end=" ")
                drones_zones[drone.zone] += 1
                drones_positions[drone.id] = drone.zone
                continue

            elif drone_map.zones[next_zone].zone == "restricted":
                if (
                    drones_zones[
                        next_zone] < drone_map.zones[next_zone].max_drones
                    and conn_capacity[(drone.zone, next_zone)] < max_capacity
                ):
                    current_zone = drone.zone
                    drone.in_transit = True
                    drone.transit_destination = next_zone
                    drones_zones[drone.zone] -= 1
                    print(f"D{drone.id}-({current_zone}-{next_zone})", end=" ")
                    drones_positions[drone.id] = f"{current_zone}-{next_zone}"
                else:
                    continue

            else:
                if (
                    drones_zones[
                        next_zone] < drone_map.zones[next_zone].max_drones
                    and conn_capacity[(drone.zone, next_zone)] < max_capacity
                ):
                    conn_capacity[(drone.zone, next_zone)] += 1
                    drones_zones[drone.zone] -= 1
                    drone.move()
                    print(f"D{drone.id}-{drone.zone}", end=" ")
                    drones_zones[drone.zone] += 1
                    drones_positions[drone.id] = drone.zone
                else:
                    continue

        history.append(dict(drones_positions))

        print()
        turns += 1

    return history
