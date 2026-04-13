"""Spinning ASCII donut — Andy Sloane's donut.c ported to half-block cells.

Geometry mirrors the deobfuscated donut.c: a torus of inner radius 1 and
outer radius 2 is rotated about the X axis (angle A) and Z axis (angle B),
perspective-projected, and lit by a diagonal light source.

Instead of the original 12-character luminance ramp, the surface is
rendered as multi-colored "sprinkles": each lit point picks a palette
from THEME_ORDER based on its position on the torus plus a slowly
advancing frame offset, so colors appear to march around the donut as
it spins. Within each palette, the Lambertian intensity picks the shade
so shape and depth still read cleanly.
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

# Frames between each advance of the sprinkle cycle. Lower = faster theme
# rotation around/across the donut.
SPRINKLE_CYCLE_FRAMES = 6

# Precomputed flat list of sprinkle palettes (one per theme). Each entry is
# the theme's 5-color lava ramp, indexed by Lambertian level.
SPRINKLE_PALETTES = [THEMES[name]['lava'] for name in THEME_ORDER]
NUM_PALETTES = len(SPRINKLE_PALETTES)

# Sprinkle patterns: (i_mult, j_mult) controls how fast the palette index
# shifts along each torus axis. B cycles forward, V cycles backward.
# Defaulting to (0, 0) means the whole donut shares one palette that
# rotates through every theme over time — the most obvious "theme
# cycling" look. Other patterns layer spatial variation on top.
#   (0, 0): solid — whole donut shifts through every theme over time
#   (1, 3): gentle rainbow bands wrapping the ring
#   (5, 1): tight vertical stripes across the tube
#   (1, 7): broad bands around the ring
#   (3, 5): diagonal confetti grid
#   (0, 1): color per ring segment (chunky wedges)
#   (1, 0): color per tube cross-section (stacked hoops)
#   (7, 7): fine speckled confetti
SPRINKLE_PATTERNS = [
    (0, 0),
    (1, 3),
    (5, 1),
    (1, 7),
    (3, 5),
    (0, 1),
    (1, 0),
    (7, 7),
]


class Donut:
    """Fullscreen spinning torus. Compatible with the app's run loop."""

    def __init__(self, width, height, speed_mult=1.0):
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
        self.sprinkle_idx = 0

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

    def next_sprinkle(self):
        """Advance to the next sprinkle pattern."""
        self.sprinkle_idx = (self.sprinkle_idx + 1) % len(SPRINKLE_PATTERNS)

    def prev_sprinkle(self):
        """Go back to the previous sprinkle pattern."""
        self.sprinkle_idx = (self.sprinkle_idx - 1) % len(SPRINKLE_PATTERNS)

    def render(self, screen, ch, x_off=0, y_off=0):
        w = self.width
        ph = self.phys_h
        if w <= 0 or ph <= 0:
            return

        # z-buffer and color buffer, one entry per physical half-cell
        neg_inf = -1.0e30
        n_cells = w * ph
        z = [neg_inf] * n_cells
        col_buf = [None] * n_cells  # None = background (theme liquid)

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

        # Sprinkle cycle offset: advances over time so colors rotate around
        # the torus even when the user pauses rotation.
        cycle_offset = self.frame // SPRINKLE_CYCLE_FRAMES
        i_mult, j_mult = SPRINKLE_PATTERNS[self.sprinkle_idx]

        # Iterate (j = theta around ring, i = phi around tube). We track
        # integer indices alongside the angles so each surface point gets
        # a stable palette index derived from its (i_idx, j_idx).
        j = 0.0
        j_idx = 0
        while j < two_pi:
            sinj = math.sin(j)
            cosj = math.cos(j)
            h = cosj + R2
            i = 0.0
            i_idx = 0
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
                        if L < 0.0:
                            L = 0.0
                        level = int(L * 5.0)
                        if level > 4:
                            level = 4
                        # Pick a palette from THEME_ORDER based on surface
                        # position + time, then pick the shade by lighting.
                        palette_idx = (i_idx * i_mult + j_idx * j_mult
                                       + cycle_offset) % NUM_PALETTES
                        col_buf[idx] = SPRINKLE_PALETTES[palette_idx][level]
                i += phi_step
                i_idx += 1
            j += theta_step
            j_idx += 1

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
                    # Draw solid liquid cell cheaply via the standard path
                    ch.draw_cell(screen, y_off + row, x_off + col, 0, 0)
                else:
                    ch.draw_colored_cell(screen, y_off + row, x_off + col,
                                         top, bot)
