import heapq
from typing import Dict, List, Optional, Tuple
from graph import Graph


def find_shortest_path(graph: Graph, start: str, end: str
                       ) -> Tuple[float, Optional[List[str]]]:
    """
    Finds the shortest path between two zones using Dijkstra's algorithm.

    Args:
        graph (Graph): The graph object.
        start (str): Start zone name.
        end (str): End zone name.

    Returns:
        Tuple[float, Optional[List[str]]]:
            - Total cost of the path
            - List of zone names in order, or None if no path exists
    """

    distances = {zone: float("inf") for zone in graph.zones}
    distances[start] = 0
    visited = set()
    pq: List[Tuple[float, str]] = []
    heapq.heappush(pq, (0, start))

    parent: Dict[str, Optional[str]] = {start: None}
    while pq:
        cost, zone_name = heapq.heappop(pq)
        if zone_name in visited:
            continue
        if zone_name == end:
            path = []
            current: str | None = end
            while current is not None:
                path.append(current)
                current = parent[current]
            return cost, path[::-1]

        visited.add(zone_name)

        for zone in graph.get_neighbors(zone_name):
            new_cost = cost + zone.cost
            if new_cost < distances[zone.neighbor]:
                distances[zone.neighbor] = new_cost
                heapq.heappush(pq, (new_cost, zone.neighbor))
                parent[zone.neighbor] = zone_name

    return float("inf"), None


def find_two_shortest_paths(
        graph: Graph, start: str, end: str
        ) -> List[Tuple[float, List[str]]]:

    first_cost, first_path = find_shortest_path(graph, start, end)

    if not first_path:
        return []

    best_second = None

    i = 0
    for i in range(len(first_path) - 1):

        zone1 = first_path[i]
        zone2 = first_path[i + 1]

        removed_links = graph.remove_connection(zone1, zone2)

        cost, path = find_shortest_path(graph, start, end)

        graph.restore_connection(removed_links)

        if path and path != first_path:

            if best_second is None or cost < best_second[0]:
                best_second = (cost, path)

    results = [(first_cost, first_path)]

    if best_second:
        results.append(best_second)

    return results
