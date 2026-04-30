class Link:
    def __init__(self, neighbor, cost, max_link_capacity):
        self.neighbor = neighbor
        self.cost = cost
        self.max_link_capacity = max_link_capacity


class Graph:
    def __init__(self):
        self.zones = {}
        self.connections = {}

    def add_zone(self, zone):
        self.zones[zone.name] = zone
        if zone.name not in self.connections:
            self.connections[zone.name] = []

    def get_cost(self, zone_name):
        zone = self.zones[zone_name]

        if zone.zone == "normal":
            return 1
        elif zone.zone == "priority":
            return 1
        elif zone.zone == "restricted":
            return 2
        elif zone.zone == "blocked":
            return float("inf")

    def add_connection(self, conn):
        z1 = conn.zone1
        z2 = conn.zone2

        cost_to_z2 = self.get_cost(z2)
        cost_to_z1 = self.get_cost(z1)

        if cost_to_z1 == float("inf") or cost_to_z2 == float("inf"):
            return
        
        link1 = Link(z2, cost_to_z2, conn.max_link_capacity)
        link2 = Link(z1, cost_to_z1, conn.max_link_capacity)

        self.connections[z1].append(link1)
        self.connections[z2].append(link2)

    def get_neighbors(self, zone_name):
        return self.connections.get(zone_name, [])
