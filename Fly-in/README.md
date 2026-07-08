# Fly-in Drones

*This project has been created as part of the 42 curriculum by aessabri42.*

---

## Description

**Fly-in Drones** is a drone routing simulation project. The goal is to move all drones from a start zone to an end zone in the fewest possible simulation turns, while respecting zone capacities, connection constraints, and movement costs.

The project reads a custom map file format that defines zones, connections, and drone counts, then computes optimal paths and simulates the movement of all drones turn by turn.

Key features:
- Custom map parser with full error handling
- Graph construction with weighted edges
- Multi-path Dijkstra-based pathfinding
- Turn-based simulation engine respecting all capacity and movement rules
- Pygame-based graphical visualization of the drone network and simulation

---

## Instructions

### Requirements

- Python 3.10+
- pygame

Install dependencies:

```bash
pip install pygame
```

### Running the project

```bash
python3 main.py <map_file>
or simply:
make run
```

Example:

```bash
python3 main.py maps/easy1.txt
```

The program will:
1. Parse and validate the map file
2. Run the simulation and print the turn-by-turn output
3. Open a graphical visualization window

### Map file format

```
nb_drones: 3
start_hub: start 0 0 [color=green max_drones=3]
hub: waypoint 1 0 [zone=normal color=blue]
end_hub: goal 2 0 [color=red max_drones=3]
connection: start-waypoint
connection: waypoint-goal
```

---

## Algorithm Choices and Implementation Strategy

### Parsing
The parser reads the map file line by line, validates the syntax and semantics, and builds a `DroneMap` object containing all zones, connections, and metadata. Errors are reported with a clear message and the program exits immediately.

### Graph Construction
Zones and connections are converted into an adjacency list (`Graph` class). Each edge (`Link`) stores the neighbor name, movement cost, and max link capacity. Movement cost is based on the destination zone type:
- `normal` → 1 turn
- `priority` → 0.9 turns (preferred)
- `restricted` → 2 turns
- `blocked` → inaccessible

### Pathfinding
**Dijkstra's algorithm** is used to find the shortest path from start to end based on weighted movement costs. A `find_all_paths` function extends this by temporarily removing connections from the graph and re-running Dijkstra to discover alternative routes. Paths are stored as `(cost, path)` tuples.

### Drone Distribution
Paths are stored in a **min-heap** (priority queue). Each drone is assigned the path with the lowest current cost. After assignment, the cost of that path is incremented by its length, encouraging even distribution across paths (greedy round-robin by cost).

### Simulation Engine
The simulation runs turn by turn:
- Each drone attempts to move to the next zone in its assigned path
- Zone capacity (`max_drones`) and connection capacity (`max_link_capacity`) are checked before each move
- Restricted zones require 2 turns to enter: the drone enters a `in_transit` state on turn 1 and arrives on turn 2
- Drones that cannot move wait in place
- The simulation ends when all drones reach the end zone


## Visual Representation

The visualization is built with **pygame** and displays:

- **Zones** as colored circles using the colors defined in the map file
- **Connections** as black lines between zones
- **Zone names** rendered inside each circle
- **Drone positions** updated each turn, showing drone IDs below their current zone
- **Turn navigation** with two modes:
  - Manual mode: use buttons to step forward/backward through turns
  - Auto mode: drones move automatically turn by turn

The visualization helps users understand bottlenecks, drone distribution across paths, and the effect of zone/connection capacity constraints on overall performance.

---

## Resources

### Pathfinding & Graph Theory
- [Dijkstra's Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python heapq documentation](https://docs.python.org/3/library/heapq.html)


### AI Usage
AI was used as a learning and guidance tool throughout this project. Specifically:
- To understand and explain core concepts such as Dijkstra's algorithm, priority queues, adjacency lists, and graph traversal
- To guide the step-by-step implementation of the parser, graph, pathfinding, simulation engine, and visualizer
- To help debug issues in the simulation logic (capacity checks, restricted zone handling, transit states)
- To review code structure and suggest improvements

AI did not write the code directly — all code was written by me based on guided explanations and conceptual discussions.