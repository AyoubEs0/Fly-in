from graph import Graph
import heapq


def find_shortest_path(graph, start, end):
    distances = {zone: float("inf") for zone in graph.zones}
    distances[start] = 0
    visited = set()
    pq = []
    heapq.heappush(pq, (0, start))
    
    parent = {start: None}
    while pq:
        cost, zone_name = heapq.heappop(pq)
        if zone_name in visited:
            continue
        if zone_name == end:
            path = []
            current = end
            while current is not None:
                path.append(current)
                current = parent[current]
            return path[::-1]
        
        visited.add(zone_name)

        for zone in graph.get_neighbors(zone_name):
            new_cost = cost + zone.cost
            if new_cost < distances[zone.neighbor]:
                distances[zone.neighbor] = new_cost
                heapq.heappush(pq, (new_cost, zone.neighbor))
                parent[zone.neighbor] = zone_name
    return None
