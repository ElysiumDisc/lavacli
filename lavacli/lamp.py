"""Lava lamp simulation with metaball physics and half-block rendering."""
import curses
import math
import random

# ---------------------------------------------------------------------------
# Shape profiles: (normalized_y, normalized_width)
# y: 0 = top of glass body, 1 = bottom of glass body
# width: 0 = zero, 1 = max body width
#
# REAL lava lamps are CONICAL: narrow at top, widest at bottom.
# ---------------------------------------------------------------------------
SHAPES = {
    'classic': [  # 16.3"/52oz - the iconic lava lamp
        (0.00, 0.22), (0.05, 0.26), (0.10, 0.32), (0.15, 0.38),
        (0.20, 0.45), (0.25, 0.52), (0.30, 0.59), (0.35, 0.65),
        (0.40, 0.71), (0.45, 0.76), (0.50, 0.80), (0.55, 0.84),
        (0.60, 0.87), (0.65, 0.90), (0.70, 0.93), (0.75, 0.95),
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
}

SHAPE_ORDER = ['classic', 'slim', 'globe', 'lava', 'diamond']

# ---------------------------------------------------------------------------
# Base profile: hourglass/pedestal shape (relative to body bottom width)
# The base narrows to a waist then flares out to the foot
# ---------------------------------------------------------------------------
BASE_PROFILE = [
    (0.00, 1.00),   # top: matches body bottom width
    (0.08, 0.90),
    (0.16, 0.72),
    (0.24, 0.55),
    (0.32, 0.42),
    (0.40, 0.34),   # waist (narrowest)
    (0.48, 0.38),
    (0.56, 0.50),
    (0.64, 0.62),
    (0.72, 0.74),
    (0.80, 0.84),
    (0.88, 0.92),
    (0.94, 0.96),
    (1.00, 0.98),   # foot
]

# Cap profile (relative to body top width)
CAP_PROFILE = [
    (0.00, 0.50),   # dome top
    (0.33, 0.70),
    (0.66, 0.90),
    (1.00, 1.00),   # connects to body
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
}

FLOW_ORDER = ['classic', 'chaotic', 'zen', 'bouncy', 'swirl']

# ---------------------------------------------------------------------------
# Size presets matching real lava lamp dimensions
# ---------------------------------------------------------------------------
SIZE_DEFAULTS = {
    'S':  {'name': '11.5"',     'body_height': 14, 'body_width': 8,
            'base_height': 5, 'cap_height': 2,
            'num_balls': 3, 'ball_radius': 1.8},
    'M':  {'name': '14.5"',     'body_height': 20, 'body_width': 12,
            'base_height': 6, 'cap_height': 2,
            'num_balls': 4, 'ball_radius': 2.4},
    'L':  {'name': '16.3"',     'body_height': 26, 'body_width': 14,
            'base_height': 8, 'cap_height': 3,
            'num_balls': 5, 'ball_radius': 3.0},
    'XL': {'name': '17"',       'body_height': 30, 'body_width': 16,
            'base_height': 9, 'cap_height': 3,
            'num_balls': 6, 'ball_radius': 3.4},
    'G':  {'name': '27" Grande', 'body_height': 40, 'body_width': 22,
            'base_height': 12, 'cap_height': 3,
            'num_balls': 8, 'ball_radius': 4.5},
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
                 num_balls, ball_radius, base_height, cap_height):
        self.style = style
        self.body_width = body_width
        self.body_height = body_height
        self.phys_height = body_height * 2  # half-block vertical resolution
        self.base_height = base_height
        self.cap_height = cap_height
        self.flow_type = flow_type
        self.params = FLOW_PARAMS[flow_type]
        self.profile = SHAPES[style]
        self.ball_radius = ball_radius
        self.speed_mult = 1.0
        self.paused = False

        # Place balls mostly at bottom (they'll heat up and rise)
        self.balls = []
        for _ in range(num_balls):
            x = random.uniform(self.body_width * 0.25, self.body_width * 0.75)
            y = random.uniform(self.phys_height * 0.55, self.phys_height * 0.92)
            self.balls.append(Ball(x, y, ball_radius))

    @property
    def total_width(self):
        return self.body_width + 2  # 1 col padding each side

    @property
    def total_height(self):
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

    def _base_bounds_at(self, norm_y, body_bottom_width):
        """Base width at normalized y (0=top, 1=bottom), scaled to columns."""
        ratio = _interpolate_profile(BASE_PROFILE, norm_y)
        half = ratio * body_bottom_width / 2
        center = self.body_width / 2
        return (center - half, center + half)

    def _cap_bounds_at(self, norm_y, body_top_width):
        """Cap width at normalized y (0=top, 1=bottom), scaled to columns."""
        ratio = _interpolate_profile(CAP_PROFILE, norm_y)
        half = ratio * body_top_width / 2
        center = self.body_width / 2
        return (center - half, center + half)

    # ----- Physics -----

    def update(self):
        if self.paused:
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

            # Collide with shape walls
            left, right = self.get_body_bounds(ball.y)
            margin = 0.8
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
        total = 0.0
        for ball in self.balls:
            dx = px - ball.x
            dy = (py - ball.y) * 0.55  # slight vertical squash for organic blobs
            d_sq = dx * dx + dy * dy
            if d_sq < 0.001:
                d_sq = 0.001
            total += (ball.radius * ball.radius) / d_sq
        return total

    @staticmethod
    def field_to_level(field):
        """0=liquid, 1-5=lava intensity."""
        if field < 1.0:
            return 0
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

    def _render_body(self, screen, bx, by, bounds, ch):
        """Render the glass body with colored liquid and lava metaballs."""
        for row in range(self.body_height):
            left_col, right_col = bounds[row]
            sy = by + row

            for col in range(left_col, right_col + 1):
                sx = bx + col
                px = col + 0.5
                py_t = row * 2
                py_b = row * 2 + 1

                lt, rt = self.get_body_bounds(py_t)
                lb, rb = self.get_body_bounds(py_b)
                top_in = lt <= px <= rt
                bot_in = lb <= px <= rb

                ft = self.compute_field(px, py_t + 0.5) if top_in else 0
                fb = self.compute_field(px, py_b + 0.5) if bot_in else 0

                tl = self.field_to_level(ft) if top_in else -1
                bl = self.field_to_level(fb) if bot_in else -1

                ch.draw_cell(screen, sy, sx, tl, bl)

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
                cap_w_t = _interpolate_profile(CAP_PROFILE,
                            py_t / max(1, self.cap_height * 2)) * body_top_w
                cap_w_b = _interpolate_profile(CAP_PROFILE,
                            py_b / max(1, self.cap_height * 2)) * body_top_w
                half_t = cap_w_t / 2
                half_b = cap_w_b / 2
                center = body_top_w / 2

                t_in = (center - half_t) <= px <= (center + half_t)
                b_in = (center - half_b) <= px <= (center + half_b)

                # Highlight top rows, shadow bottom rows
                highlight = norm_y < 0.5
                ch.draw_base_cell(screen, sy, bx + col, t_in, b_in, highlight)

    def _render_base(self, screen, bx, base_y, bot_bounds, ch):
        """Render the metallic hourglass base below the glass body."""
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

                bw_t = _interpolate_profile(BASE_PROFILE,
                            py_t / max(1, self.base_height * 2)) * body_bot_w
                bw_b = _interpolate_profile(BASE_PROFILE,
                            py_b / max(1, self.base_height * 2)) * body_bot_w

                t_in = (body_bot_w / 2 - bw_t / 2) <= px <= (body_bot_w / 2 + bw_t / 2)
                b_in = (body_bot_w / 2 - bw_b / 2) <= px <= (body_bot_w / 2 + bw_b / 2)

                # Highlight the wider sections, shadow at waist
                highlight = norm_y < 0.15 or norm_y > 0.65
                ch.draw_base_cell(screen, sy, bx + col, t_in, b_in, highlight)

    # ----- Controls -----

    def add_ball(self):
        x = random.uniform(self.body_width * 0.3, self.body_width * 0.7)
        y = random.uniform(self.phys_height * 0.6, self.phys_height * 0.9)
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
