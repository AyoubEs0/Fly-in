import pygame
from typing import Dict, List, Tuple
from parsing import DroneMap


class Visualizer():
    """Visualizes the drone simulation using Pygame."""
    def __init__(self, drone_map: DroneMap) -> None:
        """
        Initializes the visualizer.

        Args:
        drone_map (DroneMap): Parsed map data.
        """
        self.drone_map = drone_map

    def get_coordinates(
            self,
            drone_map: DroneMap,
            zone_name: str,
            screen_width: int,
            screen_height: int) -> Tuple[float, float]:
        """
        Returns the screen coordinates of a zone.
        """
        X = drone_map.zones[zone_name].x
        Y = drone_map.zones[zone_name].y

        scale = 100

        x = X * scale
        y = Y * scale

        all_x = [z.x for z in drone_map.zones.values()]
        all_y = [z.y for z in drone_map.zones.values()]

        center_x = (min(all_x) + max(all_x)) / 2
        center_y = (min(all_y) + max(all_y)) / 2

        offset_x = screen_width // 2 - center_x * scale
        offset_y = screen_height // 2 - center_y * scale
        return x + offset_x, y + offset_y

    def get_color(self, drone_map: DroneMap, zone_name: str) -> pygame.Color:
        """
        Returns the display color of a zone.
        """
        zone_color = drone_map.zones[zone_name].color
        if zone_color is None:
            return pygame.Color("white")
        try:
            color = pygame.Color(zone_color)
        except ValueError:
            color = pygame.Color("white")
        return color

    def visualisation(self,
                      drone_map: DroneMap,
                      history: List[Dict[int, str]]) -> None:
        """
        Displays the drone simulation.
        """
        pygame.init()
        info = pygame.display.Info()

        SCREEN_WIDTH = info.current_w
        SCREEN_HEIGHT = info.current_h

        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption("Fly-in Visualization")

        BLACK = (0, 0, 0)

        font = pygame.font.SysFont(None, 20)

        drone_image = pygame.image.load("drone.webp")
        drone_image.set_colorkey((255, 255, 255))
        drone_image = pygame.transform.scale(drone_image, (120, 120))

        background = pygame.image.load("sky.webp")
        background = pygame.transform.scale(
            background, (SCREEN_WIDTH, SCREEN_HEIGHT))

        current_turn = -1
        running = True
        while running:
            screen.blit(background, (0, 0))

            for conn in drone_map.connections:
                zone1 = conn.zone1
                zone2 = conn.zone2
                x1, y1 = self.get_coordinates(
                    drone_map, zone1, SCREEN_WIDTH, SCREEN_HEIGHT)
                x2, y2 = self.get_coordinates(
                    drone_map, zone2, SCREEN_WIDTH, SCREEN_HEIGHT)
                pygame.draw.line(screen, BLACK, (x1, y1), (x2, y2), 2)

            for zone in drone_map.zones.keys():
                x, y = self.get_coordinates(
                    drone_map, zone, SCREEN_WIDTH, SCREEN_HEIGHT)
                color = self.get_color(drone_map, zone)
                pygame.draw.circle(screen, color, (x, y), 40)
                text = font.render(zone, True, BLACK)
                text_rect = text.get_rect(center=(x, y))
                screen.blit(text, text_rect)

            if current_turn >= 0 and current_turn < len(history):
                zone_groups: Dict[str, List[int]] = {}
                for drone_id, position in history[current_turn].items():
                    if position not in zone_groups:
                        zone_groups[position] = []
                    zone_groups[position].append(drone_id)

                for position, drones in zone_groups.items():
                    if "-" in str(position):
                        z1, z2 = position.split("-")

                        x1, y1 = self.get_coordinates(
                            drone_map, z1, SCREEN_WIDTH, SCREEN_HEIGHT)
                        x2, y2 = self.get_coordinates(
                            drone_map, z2, SCREEN_WIDTH, SCREEN_HEIGHT)

                        base_x = (x1 + x2) / 2
                        base_y = (y1 + y2) / 2

                    else:
                        base_x, base_y = self.get_coordinates(
                            drone_map, position, SCREEN_WIDTH, SCREEN_HEIGHT)

                    img_rect = drone_image.get_rect(center=(base_x, base_y))
                    screen.blit(drone_image, img_rect)

                    label = ",".join(str(d) for d in drones)

                    text = font.render(label, True, (255, 0, 0))
                    text_rect = text.get_rect(center=(base_x, base_y + 60))
                    screen.blit(text, text_rect)

            instructions = font.render(
                "LEFT : Previous  RIGHT : Next   ESC : Exit",
                True,
                (255, 255, 255)
            )
            screen.blit(instructions, (20, 20))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if event.key == pygame.K_RIGHT:
                        if current_turn < len(history) - 1:
                            current_turn += 1

                    if event.key == pygame.K_LEFT:
                        if current_turn > 0:
                            current_turn -= 1

        pygame.quit()
