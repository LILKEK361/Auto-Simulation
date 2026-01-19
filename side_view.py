import pygame

def _text(screen, font, x, y, s, color=(0,0,0)):
    screen.blit(font.render(s, True, color), (x, y))

def _bar(screen, rect, fill_ratio):
    fill_ratio = max(0.0, min(fill_ratio, 1.0))
    pygame.draw.rect(screen, (255,255,255), rect)
    pygame.draw.rect(screen, (60,60,60), rect, 1)
    inner = rect.inflate(-2, -2)
    inner.w = int(inner.w * fill_ratio)
    pygame.draw.rect(screen, (220,60,60), inner)  # schlicht, gut sichtbar

class SideView:
    def __init__(self):
        self.font = pygame.font.Font(None, 22)
        self.small = pygame.font.Font(None, 18)

    def draw(self, screen, world_rect: pygame.Rect, telemetry: dict):
        # Hintergrund
        pygame.draw.rect(screen, (250,250,250), world_rect)

        x0, y0 = world_rect.x + 20, world_rect.y + 20

        _text(screen, self.font, x0, y0, "Side View (Reifen / Traktion)")

        axle = telemetry["axle"]
        front = axle["front"]
        rear  = axle["rear"]

        # Kachel-Layout
        tile_w = world_rect.w - 40
        tile_h = 140
        gap = 18

        front_rect = pygame.Rect(x0, y0 + 40, tile_w, tile_h)
        rear_rect  = pygame.Rect(x0, front_rect.bottom + gap, tile_w, tile_h)

        self._draw_tire_tile(screen, front_rect, "Vorderreifen (Antrieb + Lenkung)", front)
        self._draw_tire_tile(screen, rear_rect, "Hinterreifen (rollend)", rear)

    def _draw_tire_tile(self, screen, r: pygame.Rect, title: str, d: dict):
        pygame.draw.rect(screen, (255,255,255), r)
        pygame.draw.rect(screen, (60,60,60), r, 2)

        _text(screen, self.font, r.x + 10, r.y + 8, title)

        mu = d["mu"]
        Fz = d["Fz"]
        Fmax = d["Fmax"]
        Fx_req = d["Fx_req"]
        Fx_eff = d["Fx_eff"]
        slip = d["slip"]

        _text(screen, self.small, r.x + 10, r.y + 40, f"mu: {mu:.2f}")
        _text(screen, self.small, r.x + 120, r.y + 40, f"Fz: {Fz:.1f} N")
        _text(screen, self.small, r.x + 260, r.y + 40, f"Fmax: {Fmax:.1f} N")

        _text(screen, self.small, r.x + 10, r.y + 65, f"Fx_req: {Fx_req:.1f} N")
        _text(screen, self.small, r.x + 160, r.y + 65, f"Fx_eff: {Fx_eff:.1f} N")

        # Slip Balken: 0..1 (alles über 1 bleibt rot voll)
        _text(screen, self.small, r.x + 10, r.y + 95, f"Slip: {slip*100:.0f} %")
        bar_rect = pygame.Rect(r.x + 90, r.y + 92, r.w - 110, 18)
        _bar(screen, bar_rect, min(slip, 1.0))
