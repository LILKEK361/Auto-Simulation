import pygame

class HUD:
    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Panel rechts
        self.panel_w = 260
        self.panel_rect = pygame.Rect(screen_w - self.panel_w, 0, self.panel_w, screen_h)

        # Fonts
        self.font = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        self.font_title = pygame.font.Font(None, 24)

        # UI-State
        self.active_tab = "Top Down"
        self.selected_surface = "Asphalt"
        self.gravity = 9.81

        # Precompute rects
        self._layout()

    def _layout(self):
        x0, y0, w = self.panel_rect.x, self.panel_rect.y, self.panel_rect.w

        pad = 10
        self.tab_h = 26
        self.tabs = {
            "Top Down": pygame.Rect(x0 + pad, y0 + pad, 70, self.tab_h),
            "Side":     pygame.Rect(x0 + pad + 75, y0 + pad, 55, self.tab_h),
            "Setting":  pygame.Rect(x0 + pad + 135, y0 + pad, 70, self.tab_h),
        }

        # Untergrund-Buttons (2 Reihen à 3)
        grid_top = y0 + pad + self.tab_h + 12
        btn_w = (w - 2*pad - 2*8) // 3
        btn_h = 24
        gap = 8

        labels = ["Dirt", "Terra", "Rasen", "Asphalt", "???", "???"]
        self.surface_buttons = []
        for i, lab in enumerate(labels):
            row = i // 3
            col = i % 3
            r = pygame.Rect(
                x0 + pad + col*(btn_w + gap),
                grid_top + row*(btn_h + 6),
                btn_w,
                btn_h
            )
            self.surface_buttons.append((lab, r))

        # Mini-Map-Box
        map_top = grid_top + 2*(btn_h + 6) + 10
        self.map_box = pygame.Rect(x0 + pad, map_top, w - 2*pad, 150)
        self.map_label = pygame.Rect(x0 + pad, map_top + 150, w - 2*pad, 22)

        # Gravity Widget
        grav_top = self.map_label.bottom + 10
        self.gravity_label = pygame.Rect(x0 + pad, grav_top, w - 2*pad, 22)
        self.btn_minus = pygame.Rect(x0 + pad, grav_top + 24, 28, 24)
        self.btn_plus  = pygame.Rect(x0 + w - pad - 28, grav_top + 24, 28, 24)
        self.gravity_value = pygame.Rect(self.btn_minus.right + 6, grav_top + 24,
                                         (w - 2*pad) - 2*28 - 12, 24)

        # Info Header + List
        info_top = self.btn_plus.bottom + 12
        self.info_header = pygame.Rect(x0 + pad, info_top, w - 2*pad, 26)

        # Zeilenfelder
        row_h = 26
        start = self.info_header.bottom + 8
        self.info_rows = []
        for k in range(9):
            self.info_rows.append(pygame.Rect(x0 + pad, start + k*(row_h + 6), w - 2*pad, row_h))

        # Footer
        self.footer = pygame.Rect(x0 + pad, self.panel_rect.bottom - 22, w - 2*pad, 18)

    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        mx, my = event.pos

        # Tabs
        for name, r in self.tabs.items():
            if r.collidepoint(mx, my):
                self.active_tab = name
                return

        # Untergründe
        for name, r in self.surface_buttons:
            if r.collidepoint(mx, my):
                self.selected_surface = name
                return

        # Gravity
        if self.btn_minus.collidepoint(mx, my):
            self.gravity = max(0.0, self.gravity - 0.1)
            return
        if self.btn_plus.collidepoint(mx, my):
            self.gravity = min(30.0, self.gravity + 0.1)
            return

    def draw(self, screen: pygame.Surface, sim_state: dict):
        # Hintergrund Panel
        pygame.draw.rect(screen, (245, 245, 245), self.panel_rect)
        pygame.draw.rect(screen, (60, 60, 60), self.panel_rect, 2)

        # Tabs
        for name, r in self.tabs.items():
            active = (name == self.active_tab)
            pygame.draw.rect(screen, (255, 230, 160) if active else (230, 230, 230), r)
            pygame.draw.rect(screen, (60, 60, 60), r, 1)
            self._blit_center(screen, self.font_small, name, r, (0, 0, 0))

        # Untergrund-Buttons
        for name, r in self.surface_buttons:
            selected = (name == self.selected_surface)
            pygame.draw.rect(screen, (210, 235, 255) if selected else (235, 235, 235), r)
            pygame.draw.rect(screen, (60, 60, 60), r, 1)
            self._blit_center(screen, self.font_small, name, r, (0, 0, 0))

        # Mini-Map
        pygame.draw.rect(screen, (255, 255, 255), self.map_box)
        pygame.draw.rect(screen, (60, 60, 60), self.map_box, 1)
        self._draw_minimap(screen, sim_state)

        pygame.draw.rect(screen, (235, 235, 235), self.map_label)
        pygame.draw.rect(screen, (60, 60, 60), self.map_label, 1)
        self._blit_center(screen, self.font_small, "Strecken Map", self.map_label, (0, 0, 0))

        # Gravity
        pygame.draw.rect(screen, (235, 235, 235), self.gravity_label)
        pygame.draw.rect(screen, (60, 60, 60), self.gravity_label, 1)
        self._blit_center(screen, self.font_small, "Erdanziehung", self.gravity_label, (0, 0, 0))

        for r, label in [(self.btn_minus, "-"), (self.btn_plus, "+")]:
            pygame.draw.rect(screen, (235, 235, 235), r)
            pygame.draw.rect(screen, (60, 60, 60), r, 1)
            self._blit_center(screen, self.font_small, label, r, (0, 0, 0))

        pygame.draw.rect(screen, (255, 255, 255), self.gravity_value)
        pygame.draw.rect(screen, (60, 60, 60), self.gravity_value, 1)
        g_txt = f"{self.gravity:.2f}"
        self._blit_center(screen, self.font_small, g_txt, self.gravity_value, (0, 0, 0))

        # Info header
        pygame.draw.rect(screen, (255, 200, 200), self.info_header)
        pygame.draw.rect(screen, (60, 60, 60), self.info_header, 1)
        self._blit_center(screen, self.font_small, "Info:", self.info_header, (0, 0, 0))

        # Info rows (aus sim_state)
        Fx = sim_state.get("forces", {}).get("Fx", 0.0)
        Fy = sim_state.get("forces", {}).get("Fy", 0.0)
        Fcent_abs = sim_state.get("corner_forces", {}).get("F_centripetal_abs", 0.0)
        Fcf_abs = sim_state.get("corner_forces", {}).get("F_centrifugal_abs", 0.0)

        info_lines = [
            f"StreckenZone: {sim_state.get('zone', 0)}",
            f"Geschwindigkeit: {sim_state.get('speed_kmh', 0):.1f} km/h",
            f"Reifenabnutzung: {sim_state.get('tire_wear', 0):.0f} / 100",
            f"G-Kräfte: {sim_state.get('g_force', 0):.2f}",
            f"Steigung: {sim_state.get('grade_percent', 0):.1f} %",
            f"Haftreibung: {sim_state.get('friction_n', 0):.1f} N",
            f"Laptime: {sim_state.get('laptime_s', 0):.2f} s",
            f"Fx (Längskraft): {Fx:.1f} N",
            f"Fy (Querkraft): {Fy:.1f} N",
            f"Zentripetal: {Fcent_abs:.1f} N",
            f"Zentrifugal: {Fcf_abs:.1f} N",
        ]

        colors = [(0, 0, 0)] * len(info_lines)
        colors[-2] = (0, 0, 255)
        colors[-1] = (0, 160, 0)

        for r, txt, col in zip(self.info_rows, info_lines, colors):
            pygame.draw.rect(screen, (255, 255, 255), r)
            pygame.draw.rect(screen, (60, 60, 60), r, 1)
            self._blit_left(screen, self.font_small, txt, r, col, pad=6)

        # Footer

    def _draw_minimap(self, screen: pygame.Surface, sim_state: dict):
        # Dummy: Kurve + Punkt, bis ihr echte Streckenpunkte habt
        r = self.map_box
        # Strecke (vereinfachte "8")
        pts = []
        for t in range(0, 361, 10):
            # Lissajous-artig, nur für Optik
            import math
            a = math.radians(t)
            x = 0.45 * math.sin(a)
            y = 0.35 * math.sin(2*a)
            pts.append((x, y))

        # normalisieren auf Box
        cx, cy = r.centerx, r.centery
        sx, sy = r.w * 0.45, r.h * 0.45
        pix = [(cx + p[0]*sx, cy + p[1]*sy) for p in pts]
        if len(pix) >= 2:
            pygame.draw.lines(screen, (0, 0, 0), False, pix, 2)

        # Fahrzeugpunkt (0..1 -> map coords), falls vorhanden
        p = sim_state.get("track_progress", 0.0)  # 0..1
        idx = int(p * (len(pix)-1))
        px, py = pix[max(0, min(idx, len(pix)-1))]
        pygame.draw.circle(screen, (220, 60, 60), (int(px), int(py)), 5)

    @staticmethod
    def _blit_center(screen, font, text, rect, color):
        surf = font.render(text, True, color)
        srect = surf.get_rect(center=rect.center)
        screen.blit(surf, srect)

    @staticmethod
    def _blit_left(screen, font, text, rect, color, pad=6):
        surf = font.render(text, True, color)
        srect = surf.get_rect(midleft=(rect.left + pad, rect.centery))
        screen.blit(surf, srect)
