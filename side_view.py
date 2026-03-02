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
        self.surface_color = {
                "Asphalt": (55, 55, 55),    # dunkelgrau
                "Terra":    (227, 83, 54),
                "Dirt":    (120, 85, 55),   # braun
                "Rasen":   (60, 130, 60),   # grün
                "Terra":   (145, 120, 80),
                "Glatt Eis": (38, 220, 206),  # optional
                "Voll Haftung": (255,0,255),  # optional
            }
        self.selected_color = "Asphalt";

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

        tire_radius= 50; 
        # Berechne die Mitte des Bereichs
        center_y = world_rect.centery
        # Teile den Bereich horizontal für die beiden Reifen
        left_center_x = world_rect.x + (world_rect.width / 4)
        right_center_x = world_rect.x + (3 * world_rect.width / 4)
        #Ground Coulor
        ground_color = self.surface_color.get(self.selected_color, (100, 100, 100))


        auto_chassie = pygame.Rect(0, 0,(  right_center_x - left_center_x ) + 150,100) 
        auto_chassie.bottomleft = (left_center_x - 75, center_y)
        pygame.draw.rect(screen,(180,180,180),auto_chassie)
    
#        front_rect = pygame.Rect(x0, y0 + 40, tile_w, tile_h)
#       rear_rect  = pygame.Rect(x0, front_rect.bottom + gap, tile_w, tile_h)
        ground = pygame.Rect(0,0,world_rect.w,  world_rect.h - (center_y + tire_radius));
        ground.topleft = (0,center_y + tire_radius );
        pygame.draw.rect(screen, ground_color,ground)


        self._draw_tire_circle(screen,(right_center_x, center_y), tire_radius,"Slip (Antrieb + Lenkung)", front)
        self._draw_tire_circle(screen,(left_center_x, center_y),tire_radius,"Slip (rollend)", rear)
       
        front_rect = pygame.Rect(x0, y0 + 40, tile_w, tile_h)
        rear_rect  = pygame.Rect(x0, front_rect.bottom + gap, tile_w, tile_h)
        
        self._draw_front_tile(screen, right_center_x, center_y, front)

        #self._draw_tire_tile(screen, front_rect, "Vorderreifen (Antrieb + Lenkung)", front)
        #self._draw_tire_tile(screen, rear_rect, "Hinterreifen (rollend)", rear)

    def _draw_front_tile(self,  screen,front_center_x, front_center_y, d: dict):
        """ Zeichnet einen Kasten mit den Front daten """
        r = pygame.Rect(0,0, 130, 180);
        r.centery = front_center_y - 200;
        r.centerx = front_center_x;


        pygame.draw.rect(screen,  (255,255,255),r);
        pygame.draw.rect(screen,  (60,60,60),r,2);

        _text(screen, self.font, r.x + 10, r.y + 8, "Front Tire")

        data_lines = [
            f"mu: {d['mu']:.2f}",
            f"Fz: {d['Fz']:.1f} N",
            f"Fmax: {d['Fmax']:.1f} N",
            f"Fx_req: {d['Fx_req']:.1f} N",
            f"Fx_eff: {d['Fx_eff']:.1f} N",

        ]

        line_y = r.y + 40
        for line in data_lines:
            _text(screen, self.small, r.x + 10, line_y, line)
            line_y += 20 # Abstand zwischen den Zeilen


    def _draw_tire_circle(self, screen, center, radius, title, d: dict):
        """Zeichnet einen Reifen als Kreis, dessen Farbe den Schlupf (Slip) anzeigt."""
        
        # 1. Slip-Wert holen (direkt für Farbe und Anzeige)
        slip = d.get("slip", 0.0)
        clipped_slip = min(1.0, abs(slip)) # Absolutwert, falls negativer Schlupf (Bremsen) auftritt
        
        # 2. Farbe berechnen (Interpolation Grün -> Gelb -> Rot)
        if clipped_slip < 0.5:
            # Grün (0.0) zu Gelb (0.5)
            interp = clipped_slip * 2.0
            r = int(0 + interp * 255)
            g = int(200 + interp * 55)
            b = 0
        else:
            # Gelb (0.5) zu Rot (1.0)
            interp = (clipped_slip - 0.5) * 2.0
            r = 255
            g = int(255 - interp * 255)
            b = 0
            
        color = (r, g, b)
        
        # 3. Zeichnen
        pygame.draw.circle(screen, color, center, radius)
        pygame.draw.circle(screen, (0, 0, 0), center, radius, 2)
        
        # 4. Titel
        title_surf = self.font.render(title, True, (0,0,0))
        title_rect = title_surf.get_rect(center=(center[0], center[1] - radius - 15))
        screen.blit(title_surf, title_rect)
        
        # 5. Schlupf-Prozentwert in der Mitte
        pct_text = f"{clipped_slip*100:.0f}%"
        # Kontrast-Check für den Text (falls es zu dunkelrot wird)
        text_color = (255, 255, 255) if (r > 150 and g < 100) else (0, 0, 0)
        
        pct_surf = self.font.render(pct_text, True, text_color)
        pct_rect = pct_surf.get_rect(center=center)
        screen.blit(pct_surf, pct_rect)

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
