import sys


class Zone:
    def __init__(self, name, x, y, zone, color, max_drones):
        self.name = name
        self.x = x
        self.y = y
        self.zone = zone
        self.color = color
        self.max_drones = max_drones


class Connection:
    def __init__(self, zone1, zone2, max_link_capacity=1):
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity


def read_file(map_file):
    try:
        with open(map_file) as file:
            lines = file.readlines()
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


def parse_metadata(metadata_str):
    
    result = {}
    
    if not metadata_str:
        return result
    
    items = metadata_str.strip().split()
    
    for item in items:
        
        if "=" not in item:
            print(f"Error: invalid metadata '{item}'")
            sys.exit(1)
        
        key, value = item.split("=", 1)
        
        if key == "zone":
            if value not in ["normal", "blocked", "restricted", "priority"]:
                print(f"Error: invalid zone type '{value}'")
                sys.exit(1)
            result["zone"] = value
        
        elif key == "color":
            result["color"] = value

        elif key == "max_drones":
            if not value.isdigit() or int(value) < 1:
                print("Error: max_drones must be positive integer")
                sys.exit(1)
            result["max_drones"] = int(value)

        elif key == "max_link_capacity":
            if not value.isdigit() or int(value) < 1:
                print("Error: max_link_capacity must be positive integer")
                sys.exit(1)
            result["max_link_capacity"] = int(value)
        
        else:
            print(f"Error: unknown metadata key '{key}'")
            sys.exit(1)

        return result
    

def extract_metadata(line):
    if "[" not in line:
        return line.strip(), None
    
    if line.count("[") != 1 or line.count("]") != 1:
        print("Error: metadata must be [ ... ]")
        sys.exit(1)

    start = line.index("[")
    end = line.index("]")

    if end < start:
        print("Error: invalid metadata format")
        sys.exit(1)

    metadata = line[start + 1: end]
    main_part = line[:start].strip()

    return main_part, metadata.strip()


def parse_zones(line):
        main_part, metadata_str = extract_metadata(line)

        if ":" not in line:
            print("Error: invalid zone line (missing :)")
            sys.exit(1)

        parts = main_part.split()
        if len(parts) != 4:
            print(f"Error: invalid zone format -> {line}")
            sys.exit(1)

        zone_type = parts[0].replace(":", "")
        name = parts[1]

        if "-" in name:
            print(f"Error: zone name '{name}' must not contain '-'")
            sys.exit(1)
        
        try:
            x = int(parts[2])
            y = int(parts[3])
        except ValueError:
            print("Error: coordinates must be integers")
            sys.exit(1)

        metadata = parse_metadata(metadata_str)

        return Zone(
            name=name,
            x=x,
            y=y,
            zone=metadata.get("zone", "normal"),
            color=metadata.get("color", None),
            max_drones=metadata.get("max_drones", 1)
        ), zone_type


def parse_connection(line):
    main_part, metadata_str = extract_metadata(line)

    if ":" not in main_part:
        print("Error: invalid connection line")
        sys.exit(1)

    right = main_part.split(":", 1)[1].strip()

    if right.count("-") != 1:
        print("Error: connection must be zone1-zone2")
        sys.exit(1)

    zone1, zone2 = right.split("-")

    zone1 = zone1.strip()
    zone2 = zone2.strip()

    if not zone1 or not zone2:
        print("Error: invalid connection names")
        sys.exit(1)

    if "-" in zone1 or "-" in zone2:
        print("Error: zone names must not contain '-'")
        sys.exit(1)

    metadata = parse_metadata(metadata_str)
    max_link_capacity = metadata.get("max_link_capacity", 1)

    return Connection(zone1, zone2, max_link_capacity)


def parse(lines):
    map_dict = {
        "nb_drones": 0,
        "zones": {},
        "start": None,
        "end": None,
        "connections": []
    }
    
    first_line = True

    for line in lines:
        
        line = line.strip()
        
        if line == "" or line.startswith("#"):
            continue
        
        if first_line:
            
            first_line = False
            
            if not line.startswith("nb_drones"):
                print("Error: first line must be nb_drones")
                sys.exit(1)
        
        if line.startswith("nb_drones"):
            
            if ":" not in line:
                print("Error: invalid line (not found :)")
                sys.exit(1)
            
            parts = line.split(":")
            
            try:
                nb_drones = int(parts[1])
            except ValueError:
                print("Error: nb_drones should be a valid integer")
                sys.exit(1)
            
            if nb_drones < 1:
                print("Error: nb_drones must be positive")
                sys.exit(1)
            
            map_dict["nb_drones"] = nb_drones
        
        elif line.startswith("start_hub") or line.startswith("end_hub") or line.startswith("hub"):
            
            zone, zone_type = parse_zones(line)
            
            if zone.name in map_dict["zones"]:
                print(f"Error: duplicate zone name '{zone.name}'")
                sys.exit(1)
            
            if zone_type == "start_hub":
                
                if map_dict["start"] is not None:
                    print("Error: duplicate start_hub")
                    sys.exit(1)
                map_dict["start"] = zone.name
            
            elif zone_type == "end_hub":
                
                if map_dict["end"] is not None:
                    print("Error: duplicate end_hub")
                    sys.exit(1)
                map_dict["end"] = zone.name
            
            map_dict["zones"][zone.name] = zone
        
        elif line.startswith("connection"):
            connection = parse_connection(line)
            map_dict["connections"].append(connection)
        
        else:
            print(f"Error: Unknown line type: {line}")
            sys.exit(1)
    
    if map_dict["nb_drones"] == 0:
        print("Error: nb_drones is missing")
        sys.exit(1)

    return map_dict


def validate(map_dict):
    
    if map_dict["start"] is None:
        print("Error: start not found")
        sys.exit(1)
    
    if map_dict["end"] is None:
        print("Error: end not found")
        sys.exit(1)
    
    exist = []
    
    for connection in map_dict["connections"]:
        
        if connection.zone1 not in map_dict["zones"]:
            print(f"Error: zone '{connection.zone1}' in connection does not exist")
            sys.exit(1)
        
        if connection.zone2 not in map_dict["zones"]:
            print(f"Error: zone '{connection.zone2}' in connection does not exist")
            sys.exit(1)
        
        if connection.zone1 == connection.zone2:
            print(f"Error: connection cannot link a zone to itself '{connection.zone1}'")
            sys.exit(1)
        
        pair = tuple(sorted([connection.zone1, connection.zone2]))
        
        if pair in exist:
            print(f"Error: there is duplicate in '{connection.zone1}-{connection.zone2}'")
            sys.exit(1)
        
        if map_dict["zones"][connection.zone1].zone == "blocked" or \
            map_dict["zones"][connection.zone2].zone == "blocked":
            print(f"Error: connection uses blocked zone '{connection.zone1}-{connection.zone2}'")
            sys.exit(1)
        
        exist.append(pair)


def main():

    if len(sys.argv) != 2:
        print(f"Error: missing argument found just {len(sys.argv)}")
        sys.exit(1)

    lines = read_file(sys.argv[1])
    map_dict = parse(lines)
    validate(map_dict)

    print(f"nb_drones: {map_dict['nb_drones']}")
    print(f"start: {map_dict['start']}")
    print(f"end: {map_dict['end']}")
    print(f"zones: {list(map_dict['zones'].keys())}")
    print(f"connection: {[(c.zone1, c.zone2) for c in map_dict['connections']]}")
