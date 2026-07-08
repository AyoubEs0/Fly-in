import heapq
from typing import Dict, List, Optional, Tuple
from graph import Graph


class PathFinder:
    """Finds shortest paths between nodes in a graph."""
    def __init__(self, graph: Graph):
        """Initialize the path finder with a graph."""
        self.graph = graph

    def find_shortest_path(self, start: str, end: str
                           ) -> Tuple[float, Optional[List[str]]]:
        """Return the shortest path and its cost using Dijkstra's algorithm."""

        distances = {zone: float("inf") for zone in self.graph.zones}
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

            for link in self.graph.get_neighbors(zone_name):
                new_cost = cost + link.cost
                if new_cost < distances[link.neighbor]:
                    distances[link.neighbor] = new_cost
                    heapq.heappush(pq, (new_cost, link.neighbor))
                    parent[link.neighbor] = zone_name

        return float("inf"), None

    def find_two_shortest_paths(self, start: str, end: str
                                ) -> List[Tuple[float, List[str]]]:
        """Return the shortest path and
        the best alternative path, if available."""

        first_cost, first_path = self.find_shortest_path(start, end)
        if not first_path:
            return []

        best_second = None

        i = 0
        for i in range(len(first_path) - 1):

            zone1 = first_path[i]
            zone2 = first_path[i + 1]

            removed_links = self.graph.remove_connection(zone1, zone2)

            cost, path = self.find_shortest_path(start, end)

            self.graph.restore_connection(removed_links)

            if path and path != first_path:

                if best_second is None or cost < best_second[0]:
                    best_second = (cost, path)

        results = [(first_cost, first_path)]

        if best_second:
            results.append(best_second)

        return results
