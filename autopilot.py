import pygame
import math

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(x, hi))

def angle_wrap(a: float) -> float:
    while a > math.pi:
        a -= 2.0 * math.pi
    while a < -math.pi:
        a += 2.0 * math.pi
    return a

class Autopilot:
    def __init__(self):
        # Lookahead als Progress-Offset (je größer -> glatter, aber weniger exakt)
        self.lookahead = 0.03

        # Steuerungsskalierung
        self.max_heading_error = math.radians(35)

        # Zielgeschwindigkeit
        self.v_target = 110.0  # ist in Pixel/s. im Hud wird mit km/h geschummelt

    def compute(self, car, track, progress: float):
        t_target = (progress + self.lookahead) % 1.0
        target = track.get_target_point(t_target)

        forward = pygame.Vector2(math.cos(car.yaw), math.sin(car.yaw)) # wohin zeigt das auto gerade
        to_target = (target - car.position)
        dist = to_target.length()
        if dist > 1e-6:
            to_target = to_target / dist
        else:
            to_target = forward

        cross = forward.x * to_target.y - forward.y * to_target.x # angle zwischen den beiden vektoren
        dot = forward.x * to_target.x + forward.y * to_target.y
        heading_error = math.atan2(cross, dot)  # [-pi, pi]

        steering_input = clamp(heading_error / self.max_heading_error, -1.0, 1.0)

        # abhänging von mu (Untergrund) / weniger grip --> langsamer
        mu = track.get_mu_for_progress(progress)

        v_des = self.v_target * clamp(mu / 0.9, 0.35, 1.0)

        v_des *= clamp(1.0 - abs(heading_error) / math.radians(60), 0.4, 1.0)

        v_err = v_des - car.velocity
        throttle_input = clamp(v_err / 50.0, -1.0, 1.0)

        return steering_input, throttle_input
