import math
G = 9.81

def build_sim_state(car, track, progress: float):
    a_lat = car.velocity * car.yaw_rate
    a_long = car.a_long
    g_force = math.sqrt(a_long*a_long + a_lat*a_lat) / G if G > 0 else 0.0

    m = getattr(car, "mass", 1200.0)
    friction_n = car.mu * m * G

    speed_kmh = car.velocity * 3.6
    zone = track.get_zone(progress)

    return {
        "zone": zone,
        "speed_kmh": speed_kmh,
        "tire_wear": car.tire_wear,
        "g_force": g_force,
        "grade_percent": 0.0,
        "friction_n": friction_n,
        "laptime_s": car.laptime_s,
        "track_progress": progress,
        "old_laptimes": car.old_laptimes,
    }
