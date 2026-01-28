import pygame

from car import Car
from track import Track
from autopilot import Autopilot
from hud import HUD
from topdown_view import TopDownView
from side_view import SideView

pygame.init()

# Fenster
WIDTH, HEIGHT = 1100, 750
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Auto Simulation (Top-Down / Side View)")
clock = pygame.time.Clock()

# Simulation-Objekte
car_obj = Car()
track = Track(center=pygame.Vector2(350, 300), scale_x=240, scale_y=160, zones=10)
autopilot = Autopilot()

# UI / Views
hud = HUD(WIDTH, HEIGHT)
topdown = TopDownView(trail_len=900)
side = SideView()

running = True
while running:
    dt = clock.tick(60) / 1000.0

    # -------- Events --------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        hud.handle_event(event)

    # -------- Untergrund aus HUD -> Track --------
    # (Starter-Variante: ein Untergrund für die gesamte Strecke)
    track.set_all_surfaces(hud.selected_surface)

    # -------- Progress auf Strecke bestimmen --------
    progress = track.find_progress_nearest(car_obj.position)

    # -------- Autopilot Inputs --------
    steering_input, throttle_input = autopilot.compute(car_obj, track, progress)

    # -------- Track-Parameter an aktueller Position --------
    zone = track.get_zone(progress)
    mu = track.get_mu_for_progress(progress)

    # -------- Fahrzeug updaten --------
    car_obj.update(dt, steering_input, throttle_input, mu, zone)

    # -------- Telemetrie fürs HUD / Views --------
    telemetry = car_obj.get_telemetry(progress)

    # -------- Render --------
    window.fill((255, 255, 255))

    # Weltbereich links vom HUD
    world_rect = pygame.Rect(0, 0, WIDTH - hud.panel_w, HEIGHT)

    if hud.active_tab == "Top Down":
        topdown.draw(
            window,
            world_rect,
            car_obj,
            telemetry,
            track=track
        )
    elif hud.active_tab == "Side":
        side.draw(window, world_rect, telemetry)
    else:
        # Setting tab: optional Platzhalter
        pygame.draw.rect(window, (255, 255, 255), world_rect)

    # HUD immer drüber zeichnen
    hud.draw(window, telemetry)

    pygame.display.flip()

pygame.quit()
