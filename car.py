import pygame
import math

RADSTAND = 55
MAX_ACCELERATION = 10.0
MAX_STEERING_ANGLE = math.radians(30)
MAX_STEERING_RATE = math.radians(50)
MASS = 1200.0
G = 9.81
LINEAR_DRAG = 0.25  # 1/s

def clamp(x, lo, hi):
    return max(lo, min(x, hi))

class Car:
    def __init__(self):
        self.position = pygame.Vector2(400, 300)
        self.velocity = 0.0
        self.yaw = 0.0
        self.steering_angle = 0.0

        self.mass = MASS
        self.mu = 0.9
        self.zone = 0
        self.laptime_s = 0.0
        self.tire_wear = 100.0

        # Telemetrie
        self.yaw_rate = 0.0
        self.a_long = 0.0
        self.a_lat = 0.0
        self.F_long = 0.0
        self.F_lat = 0.0

        # Achs-Telemetrie (wird pro Update gesetzt)
        self.axle = {
            "front": {"Fz": 0.0, "mu": self.mu, "Fmax": 0.0, "Fx_req": 0.0, "Fx_eff": 0.0, "slip": 0.0},
            "rear":  {"Fz": 0.0, "mu": self.mu, "Fmax": 0.0, "Fx_req": 0.0, "Fx_eff": 0.0, "slip": 0.0},
        }

    def update(self, dt: float, steering_input: float, throttle_input: float, mu: float, zone: int):
        if dt <= 0.0:
            return

        self.mu = float(mu)
        self.zone = int(zone)
        self.laptime_s += dt

        # 1) Lenkwinkel integrieren
        steering_rate = float(steering_input) * MAX_STEERING_RATE
        self.steering_angle += steering_rate * dt
        self.steering_angle = clamp(self.steering_angle, -MAX_STEERING_ANGLE, MAX_STEERING_ANGLE)

        # 2) Wunsch-Beschleunigung (Input)
        a_cmd = float(throttle_input) * MAX_ACCELERATION

        # 3) Traktionslimit (max. Längsbeschleunigung)
        a_mu_max = self.mu * G
        a_limited = clamp(a_cmd, -a_mu_max, a_mu_max)

        # 4) Drag
        a_drag = -LINEAR_DRAG * self.velocity
        self.a_long = a_limited + a_drag

        # 5) v integrieren
        self.velocity += self.a_long * dt
        if self.velocity < 0.0:
            self.velocity = 0.0

        # 6) yaw rate + yaw integrieren
        self.yaw_rate = (self.velocity / RADSTAND) * math.tan(self.steering_angle)
        self.yaw += self.yaw_rate * dt

        # 7) Position integrieren
        self.position.x += self.velocity * math.cos(self.yaw) * dt
        self.position.y += self.velocity * math.sin(self.yaw) * dt

        # 8) Querbeschleunigung und Kräfte (für Top-Down)
        self.a_lat = self.velocity * self.yaw_rate
        self.F_long = self.mass * self.a_long
        self.F_lat = self.mass * self.a_lat

        # 9) Reifen/Traktion als Achsmodell (Side-View)
        # Vereinfachung: statische Lastverteilung 50/50
        Fz_front = 0.5 * self.mass * G
        Fz_rear  = 0.5 * self.mass * G

        Fmax_front = self.mu * Fz_front
        Fmax_rear  = self.mu * Fz_rear

        # Frontantrieb: Antriebskraft nur vorn
        Fx_req_total = self.mass * a_cmd               # "gewünschte" Längskraft (ohne Drag)
        Fx_eff_total = clamp(Fx_req_total, -Fmax_front, Fmax_front)

        # Slip-Indikator: wie stark Wunsch über Grenze liegt (0..1+)
        eps = 1e-6
        slip_front = max(0.0, (abs(Fx_req_total) - Fmax_front) / (Fmax_front + eps))

        # Rear: keine Antriebskraft (in diesem Modell), also 0
        self.axle["front"] = {
            "Fz": Fz_front, "mu": self.mu, "Fmax": Fmax_front,
            "Fx_req": Fx_req_total, "Fx_eff": Fx_eff_total,
            "slip": slip_front
        }
        self.axle["rear"] = {
            "Fz": Fz_rear, "mu": self.mu, "Fmax": Fmax_rear,
            "Fx_req": 0.0, "Fx_eff": 0.0,
            "slip": 0.0
        }

        # 10) Verschleiß (einfach)
        wear_rate = 0.002 * abs(self.a_long) + 0.0015 * abs(self.a_lat)
        self.tire_wear = clamp(self.tire_wear - wear_rate * dt * 100.0, 0.0, 100.0)

    def get_telemetry(self, track_progress: float) -> dict:
        g_force = math.sqrt(self.a_long**2 + self.a_lat**2) / G if G > 0 else 0.0
        F_centripetal = self.F_lat
        F_centrifugal = -self.F_lat
        return {
            "zone": self.zone,
            "speed_kmh": self.velocity * 3.6,
            "tire_wear": self.tire_wear,
            "g_force": g_force,
            "grade_percent": 0.0,
            "friction_n": self.mu * self.mass * G,
            "laptime_s": self.laptime_s,
            "track_progress": track_progress,
            "forces": {"Fx": self.F_long, "Fy": self.F_lat},
            "corner_forces": {
                "F_centripetal": F_centripetal,
                "F_centrifugal": F_centrifugal,
                "F_centripetal_abs": abs(F_centripetal),
                "F_centrifugal_abs": abs(F_centrifugal),
            },
            "axle": self.axle,

        }
