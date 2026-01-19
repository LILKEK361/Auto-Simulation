import pygame
import math

def draw_arrow(screen, start: pygame.Vector2, vec: pygame.Vector2, color=(0,0,0), width=2):
    end = start + vec
    pygame.draw.line(screen, color, start, end, width)
    # Pfeilspitze
    if vec.length() > 1e-6:
        v = vec.normalize()
        left = pygame.Vector2(-v.y, v.x)
        head_len = 10
        head_w = 5
        p1 = end - v*head_len + left*head_w
        p2 = end - v*head_len - left*head_w
        pygame.draw.polygon(screen, color, [end, p1, p2])

class TopDownView:
    def __init__(self, trail_len=600):
        self.trail = []
        self.trail_len = trail_len

    def draw(self, screen, world_rect: pygame.Rect, car, telemetry: dict, track_polyline=None):
        pygame.draw.rect(screen, (255,255,255), world_rect)

        # Strecke
        if track_polyline and len(track_polyline) > 2:
            pygame.draw.lines(screen, (0,0,0), False, track_polyline, 2)

        # Trail updaten
        self.trail.append((car.position.x, car.position.y))
        if len(self.trail) > self.trail_len:
            self.trail.pop(0)

        if len(self.trail) > 2:
            pygame.draw.lines(screen, (120,120,120), False, self.trail, 2)

        # Auto (einfach als Kreis + Richtungsnase)
        p = pygame.Vector2(car.position)
        pygame.draw.circle(screen, (220,60,60), (int(p.x), int(p.y)), 6)

        nose = pygame.Vector2(math.cos(car.yaw), math.sin(car.yaw)) * 18
        pygame.draw.line(screen, (220,60,60), p, p + nose, 3)

        # Kräfte anzeigen
        Fx = telemetry["forces"]["Fx"]
        Fy = telemetry["forces"]["Fy"]
        Fcent = telemetry["corner_forces"]["F_centripetal"]
        Fcf = telemetry["corner_forces"]["F_centrifugal"]

        # Fahrzeugachsen
        ex = pygame.Vector2(math.cos(car.yaw), math.sin(car.yaw))
        ey = pygame.Vector2(-math.sin(car.yaw), math.cos(car.yaw))  # links

        # Skalierung, damit Pfeile sichtbar bleiben
        scale = 0.003  # ggf. anpassen

        F_cent_vec = ey * (Fcent * scale)
        F_cf_vec = ey * (Fcf * scale)
        F_long_vec = ex * (Fx * scale)
        F_lat_vec  = ey * (Fy * scale)

        draw_arrow(screen, p, F_cent_vec, color=(0, 160, 0), width=2)
        draw_arrow(screen, p, F_cf_vec, color=(255, 140, 0), width=2)
        draw_arrow(screen, p, F_long_vec, color=(0,0,255), width=2)  # Längskraft
        draw_arrow(screen, p, F_lat_vec,  color=(0,160,0), width=2)  # Querkraft
