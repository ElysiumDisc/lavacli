"""Spinning ASCII donut — Andy Sloane's donut.c ported to half-block cells.

Geometry mirrors the deobfuscated donut.c: a torus of inner radius 1 and
outer radius 2 is rotated about the X axis (angle A) and Z axis (angle B),
perspective-projected, and lit by a diagonal light source.

The surface is rendered using the active theme's 5-color lava palette.
Lambertian intensity drives shade selection so shape and depth read cleanly.
Press B/V to cycle shade modes; press C to change the color theme.
"""
import math

from .themes import THEMES, THEME_ORDER

# Torus params (R1 = tube radius, R2 = ring radius) match donut.c
R1 = 1.0
R2 = 2.0
K2 = 5.0  # camera distance along Z

# Rotation deltas per frame. donut.c accumulates 0.00004 / 0.00002 inside
# the 1760-char output loop, so per frame that's ~0.070 and ~0.035.
DELTA_A = 0.070
DELTA_B = 0.035

# Sampling density. Matches donut.c's original inner-loop resolution so
# the big torus reads cleanly without gaps.
DEFAULT_THETA_STEP = 0.07  # around the ring
DEFAULT_PHI_STEP = 0.02    # around the tube

# Raw world-to-screen scale as a fraction of each axis. Tuned so that
# the donut's projected diameter spans roughly 80-95% of the terminal
# across all rotation poses (the average silhouette diameter is about
# 1.5 × SCALE_X · w for an R1=1, R2=2, K2=5 torus). Width and height
# scale separately so wide terminals aren't left with a tiny donut.
SCALE_X = 0.58
SCALE_Y = 0.58

# Shade mode names shown in the HUD.
SHADE_MODE_NAMES = ['Smooth', 'Glow', 'Bold', 'Dim', 'Iced']
# Smooth : linear Lambertian → 5 palette shades
# Glow   : 5 shades + rim/specular highlight on the brightest 1/6 of L
# Bold   : high-contrast — compresses mid-tones, emphasises highlights/shadows
# Dim    : softer/darker — shifts all shades one step toward the darker end
# Iced   : pink icing on upward-facing surfaces, golden dough everywhere else

# Fixed ANSI-256 colors for the Iced shade mode (not theme-dependent).
# Dough: dark brown shadow → bright golden-yellow
ICING_DOUGH = (94, 130, 136, 178, 220)
# Icing: pale pink → light pink → fuchsia → hot pink → white specular
ICING_PINK  = (225, 219, 213, 207, 231)


class Donut:
    """Fullscreen spinning torus. Compatible with the app's run loop."""

    def __init__(self, width, height, speed_mult=1.0, theme_name=None):
        self.width = width
        self.height = height
        self.phys_h = height * 2
        self.speed_mult = speed_mult
        self.paused = False
        self.A = 0.0
        self.B = 0.0
        self.frame = 0
        self.theta_step = DEFAULT_THETA_STEP
        self.phi_step = DEFAULT_PHI_STEP
        self.shade_mode = 0
        n = width * self.phys_h
        self._z_buf = [-1.0e30] * n
        self._col_buf = [None] * n
        self.set_theme(theme_name or THEME_ORDER[0])

    def set_theme(self, theme_name):
        """Switch the palette used for rendering. Accepts any key from THEMES."""
        if theme_name not in THEMES:
            theme_name = THEME_ORDER[0]
        t = THEMES[theme_name]
        self._palette = list(t['lava'])          # 5 ANSI-256 color codes, dark→bright
        lava = t['lava']
        self._rim = t.get('rim', lava[-1])       # edge/specular highlight color

    def update(self):
        if self.paused:
            return
        self.A += DELTA_A * self.speed_mult
        self.B += DELTA_B * self.speed_mult
        self.frame += 1

    def resize(self, new_width, new_height):
        self.width = new_width
        self.height = new_height
        self.phys_h = new_height * 2
        n = new_width * self.phys_h
        self._z_buf = [-1.0e30] * n
        self._col_buf = [None] * n

    def next_shade(self):
        self.shade_mode = (self.shade_mode + 1) % len(SHADE_MODE_NAMES)

    def prev_shade(self):
        self.shade_mode = (self.shade_mode - 1) % len(SHADE_MODE_NAMES)

    def render(self, screen, ch, x_off=0, y_off=0):
        w = self.width
        ph = self.phys_h
        if w <= 0 or ph <= 0:
            return

        # z-buffer and color buffer, one entry per physical half-cell
        neg_inf = -1.0e30
        n_cells = w * ph
        z = self._z_buf
        col_buf = self._col_buf
        z[:] = [neg_inf] * n_cells
        col_buf[:] = [None] * n_cells

        # Scale width and height independently so wide terminals get a
        # wide donut. The torus's projected radius is roughly 0.75·scale
        # at most rotations, so scaling as a fraction of each axis
        # (rather than the smaller one) gives a visibly large ring
        # regardless of the terminal's aspect.
        scale_x = w * SCALE_X
        scale_y = ph * SCALE_Y
        cx = w * 0.5
        cy = ph * 0.5

        sinA = math.sin(self.A)
        cosA = math.cos(self.A)
        sinB = math.sin(self.B)
        cosB = math.cos(self.B)

        theta_step = self.theta_step
        phi_step = self.phi_step
        two_pi = 2 * math.pi

        # Hoist hot-path locals to avoid attribute lookups per pixel.
        palette = self._palette
        rim = self._rim
        shade_mode = self.shade_mode
        icing_dough = ICING_DOUGH
        icing_pink  = ICING_PINK

        # Bold shade-map: compresses mid-tones into the extremes.
        # [Lambertian level 0-4] → [palette index]
        BOLD_MAP = (0, 0, 2, 4, 4)

        j = 0.0
        while j < two_pi:
            sinj = math.sin(j)
            cosj = math.cos(j)
            h = cosj + R2
            i = 0.0
            while i < two_pi:
                sini = math.sin(i)
                cosi = math.cos(i)
                D = 1.0 / (sini * h * sinA + sinj * cosA + K2)
                t = sini * h * cosA - sinj * sinA
                px = cx + scale_x * D * (cosi * h * cosB - t * sinB)
                py = cy + scale_y * D * (cosi * h * sinB + t * cosB)
                L = ((sinj * sinA - sini * cosj * cosA) * cosB
                     - sini * cosj * sinA - sinj * cosA
                     - cosi * cosj * sinB)
                xi = int(px)
                yi = int(py)
                if 0 <= xi < w and 0 <= yi < ph:
                    idx = yi * w + xi
                    if D > z[idx]:
                        z[idx] = D
                        if L > 0.0:
                            if shade_mode == 4:   # iced: pink icing on top, dough below
                                # ny_w = world-space Y of outward surface normal.
                                # Positive → surface faces up → icing pools here.
                                ny_w = (cosj * cosi * sinB
                                        + cosj * sini * cosA * cosB
                                        - sinj * sinA * cosB)
                                if ny_w > 0.2:
                                    lvl = min(4, int((ny_w - 0.2) * 3.0 + L * 1.5))
                                    color = icing_pink[lvl]
                                else:
                                    color = icing_dough[min(4, int(L * 5.0))]
                            elif shade_mode == 1:  # glow: 5 shades + rim on top 1/6
                                lvl = int(L * 6.0)
                                color = rim if lvl >= 5 else palette[lvl if lvl < 5 else 4]
                            elif shade_mode == 2:  # bold: high contrast
                                lvl = min(4, int(L * 5.0))
                                color = palette[BOLD_MAP[lvl]]
                            elif shade_mode == 3:  # dim: shift one step darker
                                color = palette[max(0, min(4, int(L * 5.0)) - 1)]
                            else:                  # smooth (default)
                                color = palette[min(4, int(L * 5.0))]
                        else:
                            # Back-facing surface visible through z-buffer.
                            color = icing_dough[0] if shade_mode == 4 else palette[0]
                        col_buf[idx] = color
                i += phi_step
            j += theta_step

        # Blit half-block pairs. None cells fall back to the theme's
        # liquid color for a dark backdrop behind the donut.
        for row in range(self.height):
            t_row = row * 2
            b_row = t_row + 1
            t_base = t_row * w
            b_base = b_row * w if b_row < ph else -1
            for col in range(w):
                top = col_buf[t_base + col]
                bot = col_buf[b_base + col] if b_base >= 0 else None
                if top is None and bot is None:
                    ch.draw_cell(screen, y_off + row, x_off + col, 0, 0)
                else:
                    ch.draw_colored_cell(screen, y_off + row, x_off + col,
                                         top, bot)
