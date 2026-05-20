from typing import Dict, List
from parsing import Zone, Connection


class Link:
    """
    Represents a connection between two zones.
    """
    def __init__(
            self, neighbor: str, cost: float, max_link_capacity: int) -> None:
        """
        Creates a link to a neighbor zone.

        Args:
            neighbor (str): Name of the connected zone.
            cost (float): Travel cost to this zone.
            max_link_capacity (int): Maximum capacity of this link.
        """
        self.neighbor = neighbor
        self.cost = cost
        self.max_link_capacity = max_link_capacity


class Graph:
    """
    Represents a graph of zones and connections.
    """
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, List[Link]] = {}

    def add_zone(self, zone: Zone) -> None:
        """
        Adds a zone to the graph.

        Args:
            zone : Zone object with a name attribute.
        """
        self.zones[zone.name] = zone
        if zone.name not in self.connections:
            self.connections[zone.name] = []

    def get_cost(self, zone_name: str) -> float:
        """
        Returns movement cost based on zone type.

        Args:
            zone_name (str): Name of the zone.

        Returns:
            float: Cost of entering the zone.
        """
        zone = self.zones[zone_name]

        if zone.zone == "normal":
            return 1.0
        elif zone.zone == "priority":
            return 0.9
        elif zone.zone == "restricted":
            return 2.0
        elif zone.zone == "blocked":
            return float("inf")

        raise ValueError(f"Unknown zone type: {zone.zone}")

    def add_connection(self, conn: Connection) -> None:
        """
        Adds a bidirectional connection between two zones.

        Args:
            conn : Connection object with zone1, zone2, max_link_capacity.
        """
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

    def get_neighbors(self, zone_name: str) -> List[Link]:
        """
        Returns all neighbors of a zone.

        Args:
            zone_name (str): Zone name.

        Returns:
            List[Link]: List of connected links.
        """
        return self.connections.get(zone_name, [])

    def remove_connection(
            self, zone1: str, zone2: str) -> List[tuple[str, Link]]:
        """
        Temporarily removes a connection between two zones.

        Args:
            zone1 (str): First zone.
            zone2 (str): Second zone.

        Returns:
            List[tuple[str, Link]]: Removed links for restoration.
        """
        removed = []
        for link in self.connections[zone1]:
            if link.neighbor == zone2:
                removed.append((zone1, link))
                self.connections[zone1].remove(link)
                break

        for link in self.connections[zone2]:
            if link.neighbor == zone1:
                removed.append((zone2, link))
                self.connections[zone2].remove(link)
                break

        return removed

    def restore_connection(self, removed: List[tuple[str, Link]]) -> None:
        """
        Restores previously removed connections.

        Args:
            removed (List[tuple[str, Link]]): Removed links.
        """
        for zone, link in removed:
            self.connections[zone].append(link)
