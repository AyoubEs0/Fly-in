import sys
from typing import Optional, Dict, List, Tuple, Any


class Zone:
    """
    Represents a zone in the drone map.

    Attributes:
        name (str): Zone name.
        x (int): X coordinate.
        y (int): Y coordinate.
        zone (str): Zone type.
        color (str | None): Zone color.
        max_drones (int): Maximum drones allowed.
    """
    def __init__(
            self,
            name: str,
            x: int,
            y: int,
            zone: str,
            color: Optional[str],
            max_drones: int) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.zone = zone
        self.color = color
        self.max_drones = max_drones


class Connection:
    """
    Represents a connection between two zones.

    Attributes:
        zone1 (str): First zone name.
        zone2 (str): Second zone name.
        max_link_capacity (int): Maximum connection capacity.
    """
    def __init__(self,
                 zone1: str,
                 zone2: str,
                 max_link_capacity: int = 1,
                 line_number: int = 0) -> None:
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity
        self.line_number = line_number


class DroneMap:
    """
    Handles reading, parsing, and validating
    the drone map file.
    """
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.zones: Dict[str, Zone] = {}
        self.start: Optional[str] = None
        self.end: Optional[str] = None
        self.connections: List[Connection] = []

    def read_file(self, map_file: str) -> List[str]:
        """
        Reads the map file and returns its lines.

        Args:
            map_file (str): Path to the map file.

        Returns:
            list[str]: File lines.
        """
        try:
            with open(map_file) as file:
                lines = file.readlines()
                # print(lines)
                if len(lines) == 0:
                    print("Error: map file is empty")
                    sys.exit(1)
            return lines
        except FileNotFoundError:
            print("Error: map file not found")
            sys.exit(1)
        except PermissionError as e:
            print(f"Error: could not read file '{map_file}': {e}")
            sys.exit(1)

    def parse_metadata(
            self, metadata_str: str | None, line_number: int) -> Dict:
        """
        Parses metadata text into a dictionary.

        Args:
            metadata_str (str | None): Metadata text.

        Returns:
            dict: Parsed metadata values.
        """
        result: Dict[str, Any] = {}

        if not metadata_str:
            return result

        items = metadata_str.strip().split()

        for item in items:

            if "=" not in item:
                raise ValueError(
                    f"Error on line {line_number}: "
                    f"invalid metadata '{item}'"
                )

            key, value = item.split("=", 1)

            if key in result:
                raise ValueError(
                    f"Error on line {line_number}: "
                    f"duplicate metadata key '{key}'"
                )

            if key == "zone":
                if (
                    value not in ["normal",
                                  "blocked",
                                  "restricted",
                                  "priority"]
                        ):
                    raise ValueError(
                        f"Error on line {line_number}: "
                        f"invalid zone type '{value}'"
                    )
                result["zone"] = value

            elif key == "color":
                result["color"] = value

            elif key == "max_drones":
                if not value.isdigit() or int(value) < 1:
                    raise ValueError(
                        f"Error on line {line_number}: "
                        "max_drones must be positive integer"
                    )
                result["max_drones"] = int(value)

            elif key == "max_link_capacity":
                if not value.isdigit() or int(value) < 1:
                    raise ValueError(
                        f"Error on line {line_number}: "
                        "max_link_capacity must be positive integer"
                    )
                result["max_link_capacity"] = int(value)

            else:
                raise ValueError(
                    f"Error on line {line_number}: "
                    f"unknown metadata key '{key}'"
                )

        return result

    def extract_metadata(
            self, line: str, line_number: int) -> Tuple[str, Optional[str]]:
        """
        Extracts metadata from a line.

        Args:
            line (str): Input line.

        Returns:
            tuple[str, str | None]:
                Main text and metadata.
        """
        if not line.endswith("]"):
            return line.strip(), None

        start = line.rfind("[")
        end = line.rfind("]")

        if end < start:
            raise ValueError(
                f"Error on line {line_number}: "
                "invalid metadata format"
            )

        if not line.rstrip().endswith("]"):
            raise ValueError(
                f"Error on line {line_number}: "
                "metadata must be at end  of line"
            )

        metadata = line[start + 1: end]
        main_part = line[:start].strip()

        return main_part, metadata.strip()

    def parse_zones(self, line: str, line_number: int) -> Tuple[Zone, str]:
        """
        Parses a zone line.

        Args:
            line (str): Zone line.

        Returns:
            tuple[Zone, str]:
                Parsed zone object and zone type.
        """
        main_part, metadata_str = self.extract_metadata(line, line_number)

        if ":" not in main_part:
            raise ValueError(
                f"Error on line {line_number}: "
                "invalid zone line (missing ':')"
            )

        parts = main_part.split()
        if len(parts) != 4:
            raise ValueError(
                f"Error on line {line_number}: "
                f"invalid zone format -> {line}"
            )

        zone_type = parts[0].replace(":", "")
        name = parts[1]

        if "-" in name:
            raise ValueError(
                f"Error on line {line_number}: "
                f"zone name '{name}' must not contain '-'"
            )

        try:
            x = int(parts[2])
            y = int(parts[3])
        except ValueError:
            print(
                f"Error on line {line_number}: "
                "coordinates must be integers"
                )
            sys.exit(1)

        metadata = self.parse_metadata(metadata_str, line_number)

        if zone_type in ["start_hub", "end_hub"]:
            max_drones = metadata.get("max_drones", self.nb_drones)
        else:
            max_drones = metadata.get("max_drones", 1)

        return Zone(
            name=name,
            x=x,
            y=y,
            zone=metadata.get("zone", "normal"),
            color=metadata.get("color", None),
            max_drones=max_drones
        ), zone_type

    def parse_connection(self, line: str, line_number: int) -> Connection:
        """
        Parses a connection line.

        Args:
            line (str): Connection line.

        Returns:
            Connection: Parsed connection object.
        """
        main_part, metadata_str = self.extract_metadata(line, line_number)

        if ":" not in main_part:
            raise ValueError(
                f"Error on line {line_number}: "
                "invalid connection line"
            )

        right = main_part.split(":", 1)[1].strip()

        if right.count("-") != 1:
            raise ValueError(
                f"Error on line {line_number}: "
                "connection must be zone1-zone2"
            )

        zone1, zone2 = right.split("-")

        zone1 = zone1.strip()
        zone2 = zone2.strip()

        if not zone1 or not zone2:
            raise ValueError(
                f"Error on line {line_number}: "
                "invalid connection names"
            )
            sys.exit(1)

        if "-" in zone1 or "-" in zone2:
            raise ValueError(
                f"Error on line {line_number}: "
                "zone names must not contain '-'"
            )

        metadata = self.parse_metadata(metadata_str, line_number)
        max_link_capacity = metadata.get("max_link_capacity", 1)

        return Connection(zone1, zone2, max_link_capacity, line_number)

    def parse(self, lines: List[str]) -> None:
        """
        Parses all lines from the map file.

        Args:
            lines (list[str]): File lines.
        """
        first_line = True

        for line_number, line in enumerate(lines, start=1):

            line = line.split("#", 1)[0].strip()

            if not line:
                continue

            if first_line:

                first_line = False

                if not line.startswith("nb_drones"):
                    raise ValueError(
                        f"Error on line {line_number}: "
                        "first line must be nb_drones"
                    )

            if line.startswith("nb_drones"):

                if ":" not in line:
                    raise ValueError(
                        f"Error on line {line_number}: "
                        "invalid line (missing ':')"
                    )

                parts = line.split(":", 1)

                try:
                    nb_drones = int(parts[1].strip())
                except ValueError:
                    print(
                        f"Error on line {line_number}: "
                        "nb_drones should be a valid integer"
                    )
                    sys.exit(1)

                if nb_drones < 1:
                    raise ValueError(
                        f"Error on line {line_number}: "
                        "nb_drones must be positive")

                self.nb_drones = nb_drones

            elif (
                line.startswith("start_hub")
                or line.startswith("end_hub")
                or line.startswith("hub")
            ):

                zone, zone_type = self.parse_zones(line, line_number)

                if zone.name in self.zones:
                    raise ValueError(
                        f"Error on line {line_number}: "
                        f"duplicate zone name '{zone.name}'"
                    )

                if zone_type == "start_hub":

                    if self.start is not None:
                        raise ValueError(
                            f"Error on line {line_number}: "
                            "duplicate start_hub"
                        )

                    if zone.zone == "blocked":
                        raise ValueError(
                            f"Error on line {line_number}: "
                            "start_hub cannot be blocked"
                        )
                    self.start = zone.name

                if zone_type == "end_hub":

                    if self.end is not None:
                        raise ValueError(
                            f"Error on line {line_number}: "
                            "duplicate end_hub")

                    if zone.zone == "blocked":
                        raise ValueError(
                            f"Error on line {line_number}: "
                            "end_hub cannot be blocked"
                        )
                    self.end = zone.name

                self.zones[zone.name] = zone

            elif line.startswith("connection"):
                connection = self.parse_connection(line, line_number)
                self.connections.append(connection)

            else:
                raise ValueError(
                    f"Error on line {line_number}: "
                    f"Unknown line type: {line}"
                )

        if self.nb_drones == 0:
            raise ValueError("Error: nb_drones is missing")

    def validate(self) -> None:
        """
        Validates zones and connections.
        """
        if self.start is None:
            raise ValueError("Error: start not found")

        if self.end is None:
            raise ValueError("Error: end not found")

        start_zone = self.zones[self.start]
        end_zone = self.zones[self.end]

        start_coords = (start_zone.x, start_zone.y)
        end_coords = (end_zone.x, end_zone.y)

        if start_coords == end_coords:
            raise ValueError(
                "Error: start_hub and end_hub "
                "cannot share the same coordinates"
            )

        for zone in self.zones.values():
            if zone.name in (self.start, self.end):
                continue

            if (zone.x, zone.y) == start_coords:
                raise ValueError(
                    f"Error: zone '{zone.name}' "
                    "cannot share coordinates with start_hub"
                )

            if (zone.x, zone.y) == end_coords:
                raise ValueError(
                    f"Error: zone '{zone.name}' "
                    "cannot share coordinates with end_hub"
                )

        if start_zone.max_drones < self.nb_drones:
            raise ValueError(
                "Error: start_hub max_drones must be "
                "greater than or equal to nb_drones"
            )

        if end_zone.max_drones < self.nb_drones:
            raise ValueError(
                "Error: end_hub max_drones must be "
                "greater than or equal to nb_drones"
            )

        exist = []

        for connection in self.connections:

            if connection.zone1 not in self.zones:
                raise ValueError(
                    f"Error on line {connection.line_number}: "
                    f"zone '{connection.zone1}' does not exist"
                )

            if connection.zone2 not in self.zones:
                raise ValueError(
                    f"Error on line {connection.line_number}: "
                    f"zone '{connection.zone2}' does not exist"
                )

            if connection.zone1 == connection.zone2:
                raise ValueError(
                    f"Error on line {connection.line_number}: "
                    "connection cannot link a zone to itself "
                    f"'{connection.zone1}'"
                )

            pair = tuple(sorted([connection.zone1, connection.zone2]))

            if pair in exist:
                raise ValueError(
                    f"Error on line {connection.line_number}: "
                    "duplicate connection "
                    f"'{connection.zone1}-{connection.zone2}'"
                )

            if (
                self.zones[connection.zone1].zone == "blocked"
                or self.zones[connection.zone2].zone == "blocked"
            ):
                raise ValueError(
                    f"Error on line {connection.line_number}: "
                    "connection uses blocked zone "
                    f"'{connection.zone1}-{connection.zone2}'")

            exist.append(pair)


def parsing(drone_map: DroneMap) -> None:
    """
    Reads, parses, and validates the map.
    """
    if len(sys.argv) != 2:
        print(f"Error: missing argument found just {len(sys.argv)}")
        sys.exit(1)

    lines = drone_map.read_file(sys.argv[1])
    drone_map.parse(lines)
    drone_map.validate()
