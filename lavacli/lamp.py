"""Lava lamp simulation with metaball physics and half-block rendering."""
import curses
import math
import random

from .noise import fbm3

# ---------------------------------------------------------------------------
# Shape profiles: (normalized_y, normalized_width)
# y: 0 = top of glass body, 1 = bottom of glass body
# width: 0 = zero, 1 = max body width
#
# REAL lava lamps are CONICAL: narrow at top, widest at bottom.
# ---------------------------------------------------------------------------
SHAPES = {
    'classic': [  # 16.3"/52oz - the iconic lava lamp (wider glass top like real lamp)
        (0.00, 0.36), (0.05, 0.40), (0.10, 0.45), (0.15, 0.50),
        (0.20, 0.56), (0.25, 0.62), (0.30, 0.67), (0.35, 0.72),
        (0.40, 0.76), (0.45, 0.80), (0.50, 0.84), (0.55, 0.87),
        (0.60, 0.90), (0.65, 0.92), (0.70, 0.94), (0.75, 0.96),
        (0.80, 0.97), (0.85, 0.98), (0.90, 0.99), (0.95, 1.00),
        (1.00, 1.00),
    ],
    'slim': [  # 14.5"/20oz - straighter taper
        (0.00, 0.28), (0.10, 0.34), (0.20, 0.42), (0.30, 0.50),
        (0.40, 0.58), (0.50, 0.66), (0.60, 0.74), (0.70, 0.82),
        (0.80, 0.88), (0.90, 0.94), (1.00, 1.00),
    ],
    'globe': [  # Rounded/bulbous - wider in upper portion
        (0.00, 0.18), (0.05, 0.30), (0.10, 0.48), (0.15, 0.64),
        (0.20, 0.78), (0.25, 0.88), (0.30, 0.95), (0.35, 0.99),
        (0.40, 1.00), (0.50, 0.98), (0.60, 0.94), (0.70, 0.88),
        (0.80, 0.82), (0.90, 0.78), (1.00, 0.75),
    ],
    'lava': [  # Organic wavy shape
        (0.00, 0.20), (0.06, 0.30), (0.12, 0.48), (0.18, 0.62),
        (0.24, 0.74), (0.30, 0.82), (0.36, 0.86), (0.42, 0.83),
        (0.48, 0.80), (0.54, 0.84), (0.60, 0.90), (0.66, 0.94),
        (0.72, 0.97), (0.78, 0.99), (0.84, 1.00), (0.90, 0.99),
        (0.95, 0.97), (1.00, 0.95),
    ],
    'diamond': [  # Diamond/angular
        (0.00, 0.18), (0.10, 0.30), (0.20, 0.50), (0.30, 0.70),
        (0.40, 0.87), (0.50, 1.00), (0.60, 0.87), (0.70, 0.70),
        (0.80, 0.60), (0.90, 0.55), (1.00, 0.52),
    ],
    'rocket': [  # Mathmos Telstar rocket - torpedo/bullet shape, widest in middle
        (0.00, 0.30), (0.05, 0.42), (0.10, 0.54), (0.15, 0.65),
        (0.20, 0.74), (0.25, 0.82), (0.30, 0.89), (0.35, 0.94),
        (0.40, 0.98), (0.45, 1.00), (0.50, 1.00), (0.55, 0.98),
        (0.60, 0.94), (0.65, 0.89), (0.70, 0.82), (0.75, 0.74),
        (0.80, 0.65), (0.85, 0.56), (0.90, 0.48), (0.95, 0.42),
        (1.00, 0.38),
    ],
    'freestyle': [  # Full-width rectangle (no lamp frame)
        (0.00, 1.00), (1.00, 1.00),
    ],
}

SHAPE_ORDER = ['classic', 'slim', 'globe', 'lava', 'diamond', 'rocket', 'freestyle']

# Rocket-specific nose cone (pointed tip) and fin base profiles
ROCKET_CAP_PROFILE = [
    (0.00, 0.08),   # sharp pointed nose tip
    (0.15, 0.15),
    (0.30, 0.28),
    (0.45, 0.42),
    (0.60, 0.58),
    (0.75, 0.76),
    (0.90, 0.92),
    (1.00, 1.00),   # connects to glass top
]

ROCKET_BASE_PROFILE = [
    # Swept-back rocket fins: narrow body, wide fin tips
    (0.00, 0.80),   # top: connects to glass bottom
    (0.05, 0.65),
    (0.10, 0.50),
    (0.15, 0.38),
    (0.20, 0.28),
    (0.30, 0.18),   # narrow rocket body
    (0.40, 0.15),   # narrowest
    (0.50, 0.18),
    (0.60, 0.28),   # fins begin flaring
    (0.70, 0.45),
    (0.80, 0.65),
    (0.88, 0.82),
    (0.94, 0.94),
    (1.00, 1.00),   # wide fin tips on surface
]

# ---------------------------------------------------------------------------
# Base profile: hourglass/pedestal shape (relative to body bottom width)
# The base narrows to a waist then flares out to the foot
# ---------------------------------------------------------------------------
BASE_PROFILE = [
    # Classic Lava Original hourglass base: cone narrows to waist, flares to foot
    # Matches the real 16.3" silver aluminum base proportions
    (0.00, 1.00),   # top: cups the glass bottom (widest upper point)
    (0.04, 0.92),
    (0.08, 0.82),
    (0.12, 0.72),
    (0.16, 0.63),   # upper cone tapers quickly
    (0.20, 0.55),
    (0.24, 0.48),
    (0.28, 0.43),
    (0.32, 0.39),
    (0.36, 0.36),
    (0.40, 0.34),   # waist (narrowest) -- prominent pinch like real lamp
    (0.44, 0.34),
    (0.48, 0.36),
    (0.52, 0.39),
    (0.56, 0.44),
    (0.60, 0.50),   # lower cone flares outward
    (0.64, 0.57),
    (0.68, 0.64),
    (0.72, 0.72),
    (0.76, 0.79),
    (0.80, 0.85),
    (0.84, 0.90),
    (0.88, 0.94),
    (0.92, 0.97),
    (0.96, 0.99),
    (1.00, 1.00),   # wide stable foot
]

# Cap profile (relative to body top width)
CAP_PROFILE = [
    # Cylindrical collar/band cap (like the real silver cap on Lava Original)
    # Wide and flat, not a pointy dome -- sits like a lid on the glass
    (0.00, 0.65),   # top edge: slightly narrower than bottom
    (0.20, 0.72),
    (0.40, 0.80),
    (0.60, 0.88),
    (0.80, 0.95),
    (1.00, 1.00),   # connects to body top
]

# ---------------------------------------------------------------------------
# Flow physics parameters
# ---------------------------------------------------------------------------
FLOW_PARAMS = {
    'classic': {
        'gravity': 0.008, 'buoyancy': 0.018, 'damping': 0.98,
        'random_force': 0.003, 'swirl': 0.0, 'bounce': 0.6,
        'heat_rate': 0.012, 'cool_rate': 0.008,
    },
    'chaotic': {
        'gravity': 0.012, 'buoyancy': 0.026, 'damping': 0.97,
        'random_force': 0.012, 'swirl': 0.0, 'bounce': 0.7,
        'heat_rate': 0.018, 'cool_rate': 0.014,
    },
    'zen': {
        'gravity': 0.004, 'buoyancy': 0.010, 'damping': 0.99,
        'random_force': 0.001, 'swirl': 0.0, 'bounce': 0.4,
        'heat_rate': 0.006, 'cool_rate': 0.004,
    },
    'bouncy': {
        'gravity': 0.010, 'buoyancy': 0.022, 'damping': 0.995,
        'random_force': 0.005, 'swirl': 0.0, 'bounce': 0.92,
        'heat_rate': 0.014, 'cool_rate': 0.010,
    },
    'swirl': {
        'gravity': 0.006, 'buoyancy': 0.014, 'damping': 0.98,
        'random_force': 0.003, 'swirl': 0.02, 'bounce': 0.6,
        'heat_rate': 0.010, 'cool_rate': 0.007,
    },
    'liquid': {
        # Perlin noise flow -- params control noise characteristics
        'gravity': 0.0, 'buoyancy': 0.0, 'damping': 0.0,
        'random_force': 0.0, 'swirl': 0.0, 'bounce': 0.0,
        'heat_rate': 0.0, 'cool_rate': 0.0,
        'noise_scale': 0.06, 'noise_speed': 0.012, 'noise_octaves': 3,
    },
}

FLOW_ORDER = ['classic', 'chaotic', 'zen', 'bouncy', 'swirl', 'liquid']

# ---------------------------------------------------------------------------
# Size presets matching real lava lamp dimensions
# ---------------------------------------------------------------------------
SIZE_DEFAULTS = {
    # Proportions: glass ~55%, base ~35%, cap ~10% (like real lava lamps)
    'S':  {'name': '11.5"',     'body_height': 12, 'body_width': 8,
            'base_height': 7, 'cap_height': 2,
            'num_balls': 4, 'ball_radius': 1.8},
    'M':  {'name': '14.5"',     'body_height': 16, 'body_width': 12,
            'base_height': 10, 'cap_height': 2,
            'num_balls': 6, 'ball_radius': 2.4},
    'L':  {'name': '16.3"',     'body_height': 20, 'body_width': 14,
            'base_height': 12, 'cap_height': 3,
            'num_balls': 7, 'ball_radius': 3.0},
    'XL': {'name': '17"',       'body_height': 24, 'body_width': 16,
            'base_height': 14, 'cap_height': 3,
            'num_balls': 8, 'ball_radius': 3.4},
    'G':  {'name': '27" Grande', 'body_height': 30, 'body_width': 22,
            'base_height': 18, 'cap_height': 4,
            'num_balls': 10, 'ball_radius': 4.5},
}

SIZE_ORDER = ['S', 'M', 'L', 'XL', 'G']
SIZE_NAMES = {k: v['name'] for k, v in SIZE_DEFAULTS.items()}


# ---------------------------------------------------------------------------
# Interpolation helper
# ---------------------------------------------------------------------------
def _interpolate_profile(profile, t):
    """Smoothstep interpolation on a [(y, width), ...] profile."""
    t = max(0.0, min(1.0, t))
    if t <= profile[0][0]:
        return profile[0][1]
    if t >= profile[-1][0]:
        return profile[-1][1]
    for i in range(len(profile) - 1):
        y0, w0 = profile[i]
        y1, w1 = profile[i + 1]
        if y0 <= t <= y1:
            s = (t - y0) / (y1 - y0) if y1 != y0 else 0
            s = s * s * (3 - 2 * s)  # smoothstep
            return w0 + s * (w1 - w0)
    return profile[-1][1]


# ---------------------------------------------------------------------------
# Ball (metaball particle)
# ---------------------------------------------------------------------------
class Ball:
    __slots__ = ('x', 'y', 'vx', 'vy', 'radius', 'temp')

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.2, 0.2)
        self.vy = random.uniform(-0.1, 0.1)
        self.radius = radius
        self.temp = random.uniform(0.2, 0.5)


# ---------------------------------------------------------------------------
# Lamp
# ---------------------------------------------------------------------------
class Lamp:

    def __init__(self, style, body_width, body_height, flow_type,
                 num_balls, ball_radius, base_height, cap_height,
                 freestyle=False):
        self.style = style
        self.freestyle = freestyle
        self.body_width = body_width
        self.body_height = body_height
        self.phys_height = body_height * 2  # half-block vertical resolution
        self.base_height = 0 if freestyle else base_height
        self.cap_height = 0 if freestyle else cap_height
        self.flow_type = flow_type
        self.params = FLOW_PARAMS[flow_type]
        self.profile = SHAPES[style]
        self.ball_radius = ball_radius
        self.speed_mult = 1.0
        self.paused = False
        self._noise_time = random.uniform(0, 100)  # random start for variety

        # Place balls inside the glass area (not the metallic frame)
        self.balls = []
        for _ in range(num_balls):
            y = random.uniform(self.phys_height * 0.55, self.phys_height * 0.90)
            gl, gr = self.get_glass_bounds(y)
            x = random.uniform(gl + 0.5, gr - 0.5)
            self.balls.append(Ball(x, y, ball_radius))

    @property
    def total_width(self):
        if self.freestyle:
            return self.body_width
        return self.body_width + 2  # 1 col padding each side

    @property
    def total_height(self):
        if self.freestyle:
            return self.body_height
        return self.cap_height + self.body_height + self.base_height

    # ----- Shape queries -----

    def get_body_width_at(self, norm_y):
        """Body width ratio (0-1) at normalized y (0=top, 1=bottom)."""
        return _interpolate_profile(self.profile, norm_y)

    def get_body_bounds(self, phys_y):
        """(left, right) x bounds in body at physical y."""
        norm_y = phys_y / self.phys_height
        w = self.get_body_width_at(norm_y)
        half = w * self.body_width / 2
        center = self.body_width / 2
        return (center - half, center + half)

    def compute_body_screen_bounds(self):
        """Integer column bounds for each body row."""
        bounds = []
        for row in range(self.body_height):
            py_t = row * 2
            py_b = row * 2 + 1
            lt, rt = self.get_body_bounds(py_t)
            lb, rb = self.get_body_bounds(py_b)
            left = int(math.ceil(min(lt, lb)))
            right = int(math.floor(max(rt, rb))) - 1
            left = max(0, left)
            right = min(self.body_width - 1, right)
            bounds.append((left, right))

        # Smooth: adjacent rows differ by at most 1 col
        for i in range(1, len(bounds)):
            l, r = bounds[i]
            pl, pr = bounds[i - 1]
            l = max(l, pl - 1); l = min(l, pl + 1)
            r = min(r, pr + 1); r = max(r, pr - 1)
            if r < l:
                m = (l + r) // 2
                l, r = m, m
            bounds[i] = (l, r)
        return bounds

    def get_glass_bounds(self, phys_y):
        """Inner glass bounds (1 char inside the metallic frame on each side).
        Lava can only exist within these bounds."""
        left, right = self.get_body_bounds(phys_y)
        if self.freestyle:
            return (left, right)
        return (left + 1.0, right - 1.0)

    def _base_bounds_at(self, norm_y, body_bottom_width):
        """Base width at normalized y (0=top, 1=bottom), scaled to columns."""
        profile = ROCKET_BASE_PROFILE if self.style == 'rocket' else BASE_PROFILE
        ratio = _interpolate_profile(profile, norm_y)
        half = ratio * body_bottom_width / 2
        center = self.body_width / 2
        return (center - half, center + half)

    def _cap_bounds_at(self, norm_y, body_top_width):
        """Cap width at normalized y (0=top, 1=bottom), scaled to columns.
        Returns bounds in LOCAL coords (relative to top_left of body)."""
        profile = ROCKET_CAP_PROFILE if self.style == 'rocket' else CAP_PROFILE
        ratio = _interpolate_profile(profile, norm_y)
        half = ratio * body_top_width / 2
        center = body_top_width / 2
        return (center - half, center + half)

    # ----- Physics -----

    def update(self):
        if self.paused:
            return

        # Liquid flow: just advance noise time, no ball physics
        if self.flow_type == 'liquid':
            speed = self.params.get('noise_speed', 0.012)
            self._noise_time += speed * self.speed_mult
            return

        p = self.params
        sm = self.speed_mult

        for ball in self.balls:
            ball.vy += p['gravity'] * sm
            ball.vy -= p['buoyancy'] * ball.temp * sm

            # Temperature: heat at bottom, cool at top
            ny = ball.y / self.phys_height
            if ny > 0.75:
                ball.temp = min(1.0, ball.temp + p['heat_rate'] * sm)
            elif ny < 0.25:
                ball.temp = max(0.0, ball.temp - p['cool_rate'] * sm)
            else:
                ball.temp = max(0.0, ball.temp - p['cool_rate'] * 0.3 * sm)

            ball.vx += random.gauss(0, p['random_force']) * sm
            ball.vy += random.gauss(0, p['random_force'] * 0.5) * sm

            if p['swirl'] > 0:
                cx, cy = self.body_width / 2, self.phys_height / 2
                dx, dy = ball.x - cx, ball.y - cy
                ball.vx += -dy * p['swirl'] * sm
                ball.vy += dx * p['swirl'] * sm

            ball.vx *= p['damping']
            ball.vy *= p['damping']
            ball.x += ball.vx * sm
            ball.y += ball.vy * sm

            # Collide with GLASS walls (inside the metallic frame)
            left, right = self.get_glass_bounds(ball.y)
            margin = 0.5
            if ball.x < left + margin:
                ball.x = left + margin
                ball.vx = abs(ball.vx) * p['bounce']
            elif ball.x > right - margin:
                ball.x = right - margin
                ball.vx = -abs(ball.vx) * p['bounce']
            if ball.y < 1.0:
                ball.y = 1.0
                ball.vy = abs(ball.vy) * p['bounce']
            elif ball.y > self.phys_height - 1.0:
                ball.y = self.phys_height - 1.0
                ball.vy = -abs(ball.vy) * p['bounce']

    # ----- Metaball field -----

    def compute_field(self, px, py):
        if self.flow_type == 'liquid':
            return self._compute_noise_field(px, py)
        total = 0.0
        for ball in self.balls:
            dx = px - ball.x
            dy = (py - ball.y) * 0.55  # slight vertical squash for organic blobs
            d_sq = dx * dx + dy * dy
            if d_sq < 0.001:
                d_sq = 0.001
            total += (ball.radius * ball.radius) / d_sq
        return total

    def _compute_noise_field(self, px, py):
        """Perlin noise field for liquid flow. Returns value in metaball-compatible range."""
        scale = self.params.get('noise_scale', 0.06)
        octaves = self.params.get('noise_octaves', 3)
        n = fbm3(px * scale, py * scale * 0.7, self._noise_time, octaves)
        # Map noise [-1,1] to field [0, ~6] so field_to_level works naturally
        # noise > 0 becomes lava, noise < 0 becomes liquid
        return max(0.0, (n + 0.3) * 5.0)

    RIM_THRESHOLD = 0.55

    @staticmethod
    def field_to_level(field):
        """0=liquid, 1-5=lava intensity, 6=rim (glow edge)."""
        if field < Lamp.RIM_THRESHOLD:
            return 0
        elif field < 1.0:
            return 6   # rim: glowing edge around blobs
        elif field < 1.5:
            return 1
        elif field < 2.2:
            return 2
        elif field < 3.2:
            return 3
        elif field < 4.5:
            return 4
        else:
            return 5

    # ----- Rendering -----

    def render(self, screen, x_off, y_off, ch):
        """Render the complete lamp at (x_off, y_off). ch = ColorHelper."""
        body_bounds = self.compute_body_screen_bounds()
        body_x = x_off + 1   # 1 col padding for border
        body_y = y_off + self.cap_height

        # 1. Render cap (solid metallic)
        self._render_cap(screen, body_x, y_off, body_bounds[0], ch)

        # 2. Render body (liquid + lava)
        self._render_body(screen, body_x, body_y, body_bounds, ch)

        # 3. Render base (solid metallic hourglass)
        self._render_base(screen, body_x, body_y + self.body_height,
                          body_bounds[-1], ch)

    def render_freestyle(self, screen, x_off, y_off, ch):
        """Render fullscreen lava with no lamp frame."""
        for row in range(self.body_height):
            py_t = row * 2
            py_b = row * 2 + 1
            sy = y_off + row
            for col in range(self.body_width):
                px = col + 0.5
                ft = self.compute_field(px, py_t + 0.5)
                fb = self.compute_field(px, py_b + 0.5)
                tl = self.field_to_level(ft)
                bl = self.field_to_level(fb)
                ch.draw_cell(screen, sy, x_off + col, tl, bl)

    def _render_body(self, screen, bx, by, bounds, ch):
        """Render the glass body: metallic frame border + liquid + lava inside."""
        for row in range(self.body_height):
            outer_left, outer_right = bounds[row]
            sy = by + row
            inner_left = outer_left + 1
            inner_right = outer_right - 1

            # If body is too narrow for glass interior, fill entirely with metal
            if inner_left > inner_right:
                for col in range(outer_left, outer_right + 1):
                    ch.draw_base_cell(screen, sy, bx + col, True, True, True)
                continue

            # -- Dark glass frame outline: left and right border columns --
            py_t, py_b = row * 2, row * 2 + 1
            lt, rt = self.get_body_bounds(py_t)
            lb, rb = self.get_body_bounds(py_b)
            ol_px = outer_left + 0.5
            or_px = outer_right + 0.5
            l_top_in = lt <= ol_px <= rt
            l_bot_in = lb <= ol_px <= rb
            ch.draw_frame_cell(screen, sy, bx + outer_left,
                               l_top_in, l_bot_in)
            r_top_in = lt <= or_px <= rt
            r_bot_in = lb <= or_px <= rb
            ch.draw_frame_cell(screen, sy, bx + outer_right,
                               r_top_in, r_bot_in)

            # -- Glass interior: liquid background + lava metaballs --
            for col in range(inner_left, inner_right + 1):
                px = col + 0.5

                # Check glass bounds at each half-row
                glt, grt = self.get_glass_bounds(py_t)
                glb, grb = self.get_glass_bounds(py_b)
                top_in = glt <= px <= grt
                bot_in = glb <= px <= grb

                ft = self.compute_field(px, py_t + 0.5) if top_in else 0
                fb = self.compute_field(px, py_b + 0.5) if bot_in else 0

                tl = self.field_to_level(ft) if top_in else -1
                bl = self.field_to_level(fb) if bot_in else -1

                ch.draw_cell(screen, sy, bx + col, tl, bl)

    def _render_cap(self, screen, bx, y_off, top_bounds, ch):
        """Render the small metallic cap above the glass body."""
        top_left, top_right = top_bounds
        body_top_w = top_right - top_left + 1

        for row in range(self.cap_height):
            norm_y = row / max(1, self.cap_height - 1) if self.cap_height > 1 else 1.0
            cl, cr = self._cap_bounds_at(norm_y, body_top_w)
            left = int(math.ceil(cl)) + top_left
            right = int(math.floor(cr)) - 1 + top_left
            left = max(0, left)
            right = min(self.body_width - 1, right)
            sy = y_off + row

            for col in range(left, right + 1):
                # Use half-block rendering for smooth edges
                py_t = row * 2
                py_b = row * 2 + 1
                px = col - top_left + 0.5
                _cp = ROCKET_CAP_PROFILE if self.style == 'rocket' else CAP_PROFILE
                cap_w_t = _interpolate_profile(_cp,
                            py_t / max(1, self.cap_height * 2)) * body_top_w
                cap_w_b = _interpolate_profile(_cp,
                            py_b / max(1, self.cap_height * 2)) * body_top_w
                half_t = cap_w_t / 2
                half_b = cap_w_b / 2
                center = body_top_w / 2

                t_in = (center - half_t) <= px <= (center + half_t)
                b_in = (center - half_b) <= px <= (center + half_b)

                # 3-tone shading: bright at dome peak, mid in body, shadow at base
                if norm_y < 0.3:
                    shade = 'hi'
                elif norm_y < 0.7:
                    shade = 'mid'
                else:
                    shade = 'sh'
                ch.draw_base_cell(screen, sy, bx + col, t_in, b_in, shade=shade)

    def _render_base(self, screen, bx, base_y, bot_bounds, ch):
        """Render the metallic tapered pedestal below the glass body."""
        bot_left, bot_right = bot_bounds
        body_bot_w = bot_right - bot_left + 1

        for row in range(self.base_height):
            norm_y = row / max(1, self.base_height - 1) if self.base_height > 1 else 1.0
            bl, br = self._base_bounds_at(norm_y, body_bot_w)

            # Center relative to body
            center_offset = self.body_width / 2
            left = int(math.ceil(center_offset + bl - body_bot_w / 2))
            right = int(math.floor(center_offset + br - body_bot_w / 2)) - 1
            left = max(0, left)
            right = min(self.body_width - 1, right)
            sy = base_y + row

            for col in range(left, right + 1):
                # Half-block rendering for smooth base shape
                py_t = row * 2
                py_b = row * 2 + 1
                px = (col - center_offset) + body_bot_w / 2

                _bp = ROCKET_BASE_PROFILE if self.style == 'rocket' else BASE_PROFILE
                bw_t = _interpolate_profile(_bp,
                            py_t / max(1, self.base_height * 2)) * body_bot_w
                bw_b = _interpolate_profile(_bp,
                            py_b / max(1, self.base_height * 2)) * body_bot_w

                t_in = (body_bot_w / 2 - bw_t / 2) <= px <= (body_bot_w / 2 + bw_t / 2)
                b_in = (body_bot_w / 2 - bw_b / 2) <= px <= (body_bot_w / 2 + bw_b / 2)

                # 3-tone metallic shading matching hourglass shape:
                # hi: top collar + foot lip (widest, catch light)
                # mid: upper/lower cone slopes
                # sh: waist (narrowest, deepest shadow)
                if norm_y < 0.08:
                    shade = 'hi'    # bright collar where glass sits
                elif norm_y < 0.30:
                    shade = 'mid'   # upper cone taper
                elif norm_y < 0.55:
                    shade = 'sh'    # waist shadow (deepest)
                elif norm_y < 0.80:
                    shade = 'mid'   # lower cone flare
                else:
                    shade = 'hi'    # bright foot/lip
                ch.draw_base_cell(screen, sy, bx + col, t_in, b_in, shade=shade)

    # ----- Controls -----

    def add_ball(self):
        y = random.uniform(self.phys_height * 0.6, self.phys_height * 0.9)
        gl, gr = self.get_glass_bounds(y)
        x = random.uniform(gl + 0.5, gr - 0.5)
        self.balls.append(Ball(x, y, self.ball_radius))

    def remove_ball(self):
        if len(self.balls) > 1:
            self.balls.pop()

    def resize(self, new_width, new_height, new_base_h, new_cap_h):
        """Resize the lamp, repositioning balls proportionally."""
        old_w, old_ph = self.body_width, self.phys_height
        self.body_width = new_width
        self.body_height = new_height
        self.phys_height = new_height * 2
        self.base_height = new_base_h
        self.cap_height = new_cap_h

        for ball in self.balls:
            ball.x = ball.x * new_width / old_w if old_w > 0 else new_width / 2
            ball.y = ball.y * self.phys_height / old_ph if old_ph > 0 else self.phys_height / 2
