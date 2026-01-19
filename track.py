import pygame
import math

class Track:
    def __init__(self, center: pygame.Vector2, scale_x: float, scale_y: float, zones: int = 10):
        self.center = pygame.Vector2(center)
        self.sx = float(scale_x)
        self.sy = float(scale_y)
        self.zones = int(zones)

        self.zone_surface = ["Asphalt"] * self.zones

        self.mu_map = {
            "Asphalt": 0.90,
            "Terra":   0.60,
            "Dirt":    0.50,
            "Rasen":   0.35,
        }

        self.polyline = self._generate_polyline(400)

    def _curve(self, t: float) -> pygame.Vector2:
        """
        t in [0, 1)
        x = sin(2πt)
        y = sin(4πt) -> ergibt Acht
        """
        a = 2.0 * math.pi * t
        x = math.sin(a)
        y = math.sin(2.0 * a)
        return pygame.Vector2(self.center.x + self.sx * x, self.center.y + self.sy * y)

    def _curve_tangent(self, t: float) -> pygame.Vector2:
        """
        Ableitung (ungefähr) für Richtung (Tangentvektor).
        dx/dt ~ cos(2πt) * 2π
        dy/dt ~ cos(4πt) * 4π
        """
        a = 2.0 * math.pi * t
        dx = math.cos(a) * 2.0 * math.pi
        dy = math.cos(2.0 * a) * 4.0 * math.pi
        v = pygame.Vector2(dx, dy)
        if v.length() > 1e-9:
            v = v.normalize()
        return v

    def _generate_polyline(self, n: int):
        pts = []
        for i in range(n):
            t = i / n
            pts.append(self._curve(t))
        return pts

    def find_progress_nearest(self, pos: pygame.Vector2, samples: int = 300) -> float:
        best_t = 0.0
        best_d2 = float("inf")
        for i in range(samples):
            t = i / samples
            p = self._curve(t)
            d2 = (p - pos).length_squared()
            if d2 < best_d2:
                best_d2 = d2
                best_t = t
        return best_t

    def get_target_point(self, progress: float) -> pygame.Vector2:
        return self._curve(progress % 1.0)

    def get_tangent(self, progress: float) -> pygame.Vector2:
        return self._curve_tangent(progress % 1.0)

    def get_zone(self, progress: float) -> int:
        z = int((progress % 1.0) * self.zones)
        return max(0, min(z, self.zones - 1))

    def get_mu_for_progress(self, progress: float) -> float:
        zone = self.get_zone(progress)
        surf = self.zone_surface[zone]
        return self.mu_map.get(surf, 0.6)

    def set_all_surfaces(self, name: str):
        for i in range(self.zones):
            self.zone_surface[i] = name
