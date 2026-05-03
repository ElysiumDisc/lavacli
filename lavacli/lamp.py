"""Lava lamp simulation with metaball physics and half-block rendering."""
import curses
import math
import random
from bisect import bisect as _bisect

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
    'cylinder': [  # Straight tube style - flat sides like vintage tube lamps
        (0.00, 0.92), (0.05, 0.96), (0.10, 0.98), (0.15, 1.00),
        (0.85, 1.00), (0.90, 0.98), (0.95, 0.96), (1.00, 0.92),
    ],
    'pear': [  # Retro bulbous/pear shape - wide belly, narrow neck
        (0.00, 0.24), (0.05, 0.28), (0.10, 0.34), (0.15, 0.40),
        (0.20, 0.48), (0.25, 0.58), (0.30, 0.68), (0.35, 0.78),
        (0.40, 0.86), (0.45, 0.93), (0.50, 0.98), (0.55, 1.00),
        (0.60, 1.00), (0.65, 0.98), (0.70, 0.95), (0.75, 0.92),
        (0.80, 0.88), (0.85, 0.85), (0.90, 0.82), (0.95, 0.80),
        (1.00, 0.78),
    ],
    'rocket': [  # Mathmos Telstar rocket - cylindrical glass column, gentle tapers
        (0.00, 0.70), (0.05, 0.82), (0.10, 0.90), (0.15, 0.95),
        (0.20, 0.98), (0.25, 1.00), (0.30, 1.00), (0.35, 1.00),
        (0.40, 1.00), (0.45, 1.00), (0.50, 1.00), (0.55, 1.00),
        (0.60, 1.00), (0.65, 1.00), (0.70, 0.99), (0.75, 0.97),
        (0.80, 0.93), (0.85, 0.86), (0.90, 0.78), (0.95, 0.70),
        (1.00, 0.65),
    ],
    'freestyle': [  # Full-width rectangle (no lamp frame)
        (0.00, 1.00), (1.00, 1.00),
    ],
    'koipond': [  # Fullscreen koi pond (no lamp frame)
        (0.00, 1.00), (1.00, 1.00),
    ],
    'fireplace': [  # Fullscreen fireplace (embers rise, cool, fade)
        (0.00, 1.00), (1.00, 1.00),
    ],
    'donut': [  # Fullscreen spinning ASCII donut (no lamp frame)
        (0.00, 1.00), (1.00, 1.00),
    ],
    'campfire': [  # Fullscreen campfire with pine forest scene
        (0.00, 1.00), (1.00, 1.00),
    ],
    'xmas': [  # Fullscreen Christmas indoor fireplace
        (0.00, 1.00), (1.00, 1.00),
    ],
}

SHAPE_ORDER = ['classic', 'slim', 'globe', 'lava', 'diamond', 'cylinder', 'pear', 'rocket', 'freestyle', 'koipond', 'fireplace', 'campfire', 'donut', 'xmas']

# Rocket-specific nose cone (pointed tip) and fin base profiles
ROCKET_CAP_PROFILE = [
    # Sharper, longer nose cone — more rows near the tip so the point
    # reads at small terminal sizes
    (0.00, 0.04),   # sharp pointed nose tip
    (0.08, 0.08),
    (0.16, 0.13),
    (0.24, 0.20),
    (0.34, 0.30),
    (0.44, 0.42),
    (0.55, 0.55),
    (0.66, 0.68),
    (0.78, 0.82),
    (0.90, 0.94),
    (1.00, 1.00),   # connects to glass top
]

ROCKET_BASE_PROFILE = [
    # Three swept-back rocket fins. Profile is 1D so we suggest the fins
    # by introducing valleys in the lower half — the resulting serrated
    # silhouette reads as multiple fin tips when shaded.
    # Glass bottom is ~0.65 of body_width (matches new SHAPES['rocket']),
    # so the base top matches that.
    (0.00, 0.66),   # top: cups the wider glass bottom
    (0.04, 0.58),
    (0.08, 0.48),
    (0.12, 0.38),
    (0.16, 0.28),
    (0.22, 0.20),
    (0.30, 0.16),   # narrow rocket stem
    (0.38, 0.14),   # narrowest point
    (0.46, 0.16),
    (0.54, 0.22),   # fins begin flaring outward
    (0.60, 0.46),   # left fin tip flares out
    (0.66, 0.34),   # valley between left and center fin
    (0.72, 0.62),   # center fin tip (tallest of the three)
    (0.78, 0.40),   # valley between center and right fin
    (0.84, 0.78),   # right fin tip
    (0.90, 0.60),   # fall off below the fin tips
    (0.95, 0.40),
    (1.00, 0.32),   # narrow ground contact
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

# Cylinder/tube style: flat disc cap and simple cone base
CYLINDER_CAP_PROFILE = [
    (0.00, 0.90),   # flat disc - nearly same width top to bottom
    (0.50, 0.95),
    (1.00, 1.00),   # connects to body
]

CYLINDER_BASE_PROFILE = [
    # Simple cone base (no hourglass) like vintage tube lamps
    (0.00, 1.00),   # top: matches glass bottom
    (0.10, 0.92),
    (0.20, 0.82),
    (0.30, 0.72),
    (0.40, 0.62),
    (0.50, 0.54),
    (0.60, 0.48),
    (0.70, 0.44),
    (0.80, 0.42),   # tapers to narrow foot
    (0.90, 0.42),
    (1.00, 0.44),   # slight flare at very bottom for stability
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
    'fireplace': {
        # Embers rise, cool, fade. Internal flow used only by the
        # 'fireplace' style regardless of the user-picked flow.
        'gravity': -0.025,        # NEGATIVE = upward (rising embers)
        'buoyancy': 0.0,          # temp-based lift disabled; gravity handles it
        'damping': 0.98,
        'random_force': 0.025,    # stronger flicker/jitter
        'swirl': 0.006,           # slight updraft curl
        'bounce': 0.0,            # no wall bounce; embers exit the top
        'heat_rate': 0.0,         # spawn hot, cool monotonically
        'cool_rate': 0.022,
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
# Pre-compute y-key arrays for binary search in _interpolate_profile.
# All profile lists are small (10-25 entries); caching avoids per-call
# allocation and makes bisect actually faster than linear scan.
# ---------------------------------------------------------------------------
_PROFILE_YKEYS = {}  # id(profile_list) -> [y0, y1, ...]

def _cache_ykey(profile):
    _PROFILE_YKEYS[id(profile)] = [p[0] for p in profile]

for _v in SHAPES.values():
    _cache_ykey(_v)
for _prof in (BASE_PROFILE, CAP_PROFILE, CYLINDER_CAP_PROFILE,
              CYLINDER_BASE_PROFILE, ROCKET_CAP_PROFILE, ROCKET_BASE_PROFILE):
    _cache_ykey(_prof)
del _cache_ykey, _prof, _v

# ---------------------------------------------------------------------------
# Interpolation helper
# ---------------------------------------------------------------------------
def _interpolate_profile(profile, t):
    """Smoothstep interpolation on a [(y, width), ...] profile.
    Uses binary search on a pre-computed y-key array (cached at import time)."""
    t = max(0.0, min(1.0, t))
    if t <= profile[0][0]:
        return profile[0][1]
    if t >= profile[-1][0]:
        return profile[-1][1]
    ys = _PROFILE_YKEYS.get(id(profile))
    if ys is None:
        ys = [p[0] for p in profile]
    i = _bisect(ys, t, lo=1) - 1
    if i >= len(profile) - 1:
        i = len(profile) - 2
    y0, w0 = profile[i]
    y1, w1 = profile[i + 1]
    s = (t - y0) / (y1 - y0) if y1 != y0 else 0
    s = s * s * (3 - 2 * s)  # smoothstep
    return w0 + s * (w1 - w0)


# ---------------------------------------------------------------------------
# Ball (metaball particle)
# ---------------------------------------------------------------------------
class Ball:
    __slots__ = ('x', 'y', 'vx', 'vy', 'radius', 'temp', 'palette_id')

    def __init__(self, x, y, radius, palette_id=0):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.2, 0.2)
        self.vy = random.uniform(-0.1, 0.1)
        self.radius = radius
        self.temp = random.uniform(0.2, 0.5)
        self.palette_id = palette_id


# ---------------------------------------------------------------------------
# Lamp
# ---------------------------------------------------------------------------
class Lamp:

    def __init__(self, style, body_width, body_height, flow_type,
                 num_balls, ball_radius, base_height, cap_height,
                 freestyle=False, bicolor=False):
        self.style = style
        self.freestyle = freestyle
        self.body_width = body_width
        self.body_height = body_height
        self.phys_height = body_height * 2  # half-block vertical resolution
        self.base_height = 0 if freestyle else base_height
        self.cap_height = 0 if freestyle else cap_height
        # Fireplace forces its own internal physics regardless of flow pick
        self.flow_type = 'fireplace' if style in ('fireplace', 'campfire') else flow_type
        self.params = FLOW_PARAMS[self.flow_type]
        # Flame size for xmas style: 0=small/cozy, 1=medium, 2=large/roaring
        self.flame_size = 1
        self.profile = SHAPES[style]
        self.ball_radius = ball_radius
        self.speed_mult = 1.0
        self.paused = False
        self._noise_time = random.uniform(0, 100)  # random start for variety
        self.bicolor = bicolor
        # Trails (slow-shutter motion blur). Buffer is a grid of
        # [top_level, bot_level, frames_remaining, top_pid, bot_pid]
        # per (row, col) cell; only populated while `trails` is on.
        self.trails = False
        self.trail_buffer = None

        # Place balls inside the glass area (not the metallic frame)
        self.balls = []
        if style in ('fireplace', 'campfire'):
            # Ember cloud: many small particles spawned at the bottom, hot
            for i in range(num_balls * 2):
                x = random.gauss(body_width / 2, body_width * 0.08)
                x = max(1.0, min(body_width - 1.0, x))
                y = random.uniform(self.phys_height * 0.85,
                                   self.phys_height - 0.5)
                b = Ball(x, y, ball_radius * 0.6,
                         palette_id=(i % 2) if bicolor else 0)
                b.temp = random.uniform(0.8, 1.0)
                b.vy = random.uniform(-0.3, -0.1)  # initial upward kick
                self.balls.append(b)
        elif style == 'xmas':
            pass  # pure procedural flame — no ball physics
        else:
            for i in range(num_balls):
                y = random.uniform(self.phys_height * 0.55,
                                   self.phys_height * 0.90)
                gl, gr = self.get_glass_bounds(y)
                x = random.uniform(gl + 0.5, gr - 0.5)
                pid = (i % 2) if bicolor else 0
                self.balls.append(Ball(x, y, ball_radius, palette_id=pid))

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

    def _get_base_profile(self):
        if self.style == 'rocket':
            return ROCKET_BASE_PROFILE
        elif self.style == 'cylinder':
            return CYLINDER_BASE_PROFILE
        return BASE_PROFILE

    def _get_cap_profile(self):
        if self.style == 'rocket':
            return ROCKET_CAP_PROFILE
        elif self.style == 'cylinder':
            return CYLINDER_CAP_PROFILE
        return CAP_PROFILE

    def _base_bounds_at(self, norm_y, body_bottom_width):
        """Base width at normalized y (0=top, 1=bottom), scaled to columns."""
        profile = self._get_base_profile()
        ratio = _interpolate_profile(profile, norm_y)
        # Rocket fins extend relative to full body width so they flare wide
        ref_w = self.body_width if self.style == 'rocket' else body_bottom_width
        half = ratio * ref_w / 2
        center = self.body_width / 2
        return (center - half, center + half)

    def _cap_bounds_at(self, norm_y, body_top_width):
        """Cap width at normalized y (0=top, 1=bottom), scaled to columns.
        Returns bounds in LOCAL coords (relative to top_left of body)."""
        profile = self._get_cap_profile()
        ratio = _interpolate_profile(profile, norm_y)
        half = ratio * body_top_width / 2
        center = body_top_width / 2
        return (center - half, center + half)

    @staticmethod
    def _chrome_shade(col, body_w, norm_y, vertical_default):
        """3-tone shading that simulates chrome curvature.

        Cells near the body's vertical center column read brighter
        (chrome highlight stripe). The horizontal factor is weighted
        slightly higher than the vertical band so the stripe is
        actually visible in the body of the cap and base.
        """
        if body_w <= 1:
            return vertical_default
        dist_from_center = abs(col - (body_w - 1) / 2.0) / max(0.5, (body_w - 1) / 2.0)
        if dist_from_center < 0.22:
            horiz = 'hi'
        elif dist_from_center < 0.55:
            horiz = 'mid'
        else:
            horiz = 'sh'
        rank = {'hi': 2, 'mid': 1, 'sh': 0}
        # Weighted blend: horizontal stripe weighted 1.5x so it brightens
        # the body cells, but vertical band still gates dark waist areas.
        score = (rank[horiz] * 1.5 + rank[vertical_default]) / 2.5
        if score >= 1.5:
            return 'hi'
        elif score >= 0.5:
            return 'mid'
        return 'sh'

    # ----- Physics -----

    def update(self):
        if self.paused:
            return

        # Liquid flow: just advance noise time, no ball physics
        if self.flow_type == 'liquid':
            speed = self.params.get('noise_speed', 0.012)
            self._noise_time += speed * self.speed_mult
            return

        # Xmas: pure procedural flame — just tick noise time, no ball physics
        if self.style == 'xmas':
            self._noise_time += 0.05 * self.speed_mult
            return

        # Fireplace: inverted gravity + monotonic cooling + recycle at top
        if self.style in ('fireplace', 'campfire'):
            self._noise_time += 0.05 * self.speed_mult
            self._update_fireplace()
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

    def _update_fireplace(self):
        """Ember physics: spawn hot at bottom, rise, cool, recycle when dim."""
        p = self.params
        sm = self.speed_mult
        phys_h = self.phys_height
        for ball in self.balls:
            # Upward force (gravity is negative for fireplace)
            ball.vy += p['gravity'] * sm
            # Flicker jitter
            ball.vx += random.gauss(0, p['random_force']) * sm
            ball.vy += random.gauss(0, p['random_force'] * 0.4) * sm
            # Slight updraft curl (pulls outward as embers rise)
            if p['swirl'] > 0:
                cx = self.body_width / 2
                dx = ball.x - cx
                ball.vx += dx * p['swirl'] * sm * 0.5
            ball.vx *= p['damping']
            ball.vy *= p['damping']
            ball.x += ball.vx * sm
            ball.y += ball.vy * sm

            # Cool as a function of height: hot at bottom (t=1), cold at top.
            height_frac = max(0.0, min(1.0, 1.0 - ball.y / (phys_h * 0.75)))
            # Realistic flame shape: hotter in the center, cooler at the sides
            cx_center = self.body_width / 2
            dx_norm = abs(ball.x - cx_center) / (self.body_width / 2)
            # Center bias: side embers cool much faster (forms triangular shape)
            shape_bias = (1.0 - dx_norm) ** 1.5
            # Ease out: embers hold brightness for a while then fade near top
            ball.temp = max(0.0, ((1.0 - height_frac) ** 1.4) * shape_bias)

            # Soft horizontal wrap: nudge instead of bounce
            if ball.x < 0.5:
                ball.x = 0.5
                ball.vx = abs(ball.vx) * 0.3
            elif ball.x > self.body_width - 0.5:
                ball.x = self.body_width - 0.5
                ball.vx = -abs(ball.vx) * 0.3

            # Recycle: if an ember escaped the top or faded, respawn at bottom
            if ball.y < 0.0 or ball.temp < 0.04:
                # Spawn denser towards the center
                spawn_x = random.gauss(self.body_width / 2, self.body_width * 0.08)
                ball.x = max(1, min(self.body_width - 1, spawn_x))
                ball.y = random.uniform(phys_h * 0.90, phys_h - 0.2)
                ball.vx = random.uniform(-0.1, 0.1)
                ball.vy = random.uniform(-0.4, -0.2)
                ball.temp = random.uniform(0.9, 1.0)

    # ----- Metaball field -----

    def compute_field(self, px, py):
        if self.flow_type == 'liquid':
            return self._compute_noise_field(px, py)
        total = 0.0
        fireplace = self.style in ('fireplace', 'campfire')
        for ball in self.balls:
            dx = px - ball.x
            dy_base = (py - ball.y)
            if fireplace:
                # Flame shape: squashed bottom, long tail pointing up
                if dy_base > 0:
                    dy = dy_base * 1.2
                else:
                    dy = dy_base * 0.3
                    # Licking flame wave motion
                    dx += math.sin(self._noise_time * 2.0 + ball.x * 0.5) * dy_base * 0.4
            else:
                dy = dy_base * 0.55  # slight vertical squash for organic blobs

            d_sq = dx * dx + dy * dy
            if d_sq < 0.001:
                d_sq = 0.001
            contribution = (ball.radius * ball.radius) / d_sq
            # Fireplace: cooler embers fade out by scaling their field
            if fireplace:
                contribution *= ball.temp
            total += contribution
        
        if fireplace:
            # Sustained central flame core pillar emerging from logs
            bot = self.phys_height - 1.5
            if py < bot:
                dy_p = bot - py
                h_max = self.phys_height * 0.45
                h_frac = max(0.0, 1.0 - dy_p / h_max)
                if h_frac > 0:
                    cx = self.body_width / 2
                    # Pillar sways organically
                    sway = math.sin(self._noise_time * 2.8 - py * 0.12) * (1.0 - h_frac) * 3.5
                    dx_p = px - (cx + sway)
                    # Radius tapers: thick at base, thin at top
                    r_p = self.body_width * 0.08 * (h_frac ** 1.5)
                    if r_p > 0.1:
                        pillar_contrib = (r_p * r_p) / (dx_p * dx_p + 0.6)
                        total += pillar_contrib * (h_frac ** 0.5) * 2.5
        
        return total

    def compute_field_bicolor(self, px, py):
        """Return (total_field, dominant_palette_id) for bi-color rendering.

        Bi-color is a metaball-only feature; when flow=liquid we fall back to
        scalar field with palette_id=0 (Perlin noise has no per-ball identity).
        """
        if self.flow_type == 'liquid':
            return (self._compute_noise_field(px, py), 0)
        sum_a = 0.0
        sum_b = 0.0
        fireplace = self.style in ('fireplace', 'campfire')
        for ball in self.balls:
            dx = px - ball.x
            dy_base = (py - ball.y)
            if fireplace:
                if dy_base > 0:
                    dy = dy_base * 1.2
                else:
                    dy = dy_base * 0.3
                    dx += math.sin(self._noise_time * 2.0 + ball.x * 0.5) * dy_base * 0.4
            else:
                dy = dy_base * 0.55

            d_sq = dx * dx + dy * dy
            if d_sq < 0.001:
                d_sq = 0.001
            c = (ball.radius * ball.radius) / d_sq
            if fireplace:
                c *= ball.temp
            if ball.palette_id == 1:
                sum_b += c
            else:
                sum_a += c
        
        total = sum_a + sum_b
        if fireplace:
            # Sustained central flame core pillar (bicolor)
            bot = self.phys_height - 1.5
            if py < bot:
                dy_p = bot - py
                h_max = self.phys_height * 0.45
                h_frac = max(0.0, 1.0 - dy_p / h_max)
                if h_frac > 0:
                    cx = self.body_width / 2
                    sway = math.sin(self._noise_time * 2.8 - py * 0.12) * (1.0 - h_frac) * 3.5
                    dx_p = px - (cx + sway)
                    r_p = self.body_width * 0.08 * (h_frac ** 1.5)
                    if r_p > 0.1:
                        pillar_contrib = (r_p * r_p) / (dx_p * dx_p + 0.6)
                        total += pillar_contrib * (h_frac ** 0.5) * 2.5
        
        pid = 1 if sum_b > sum_a else 0
        return (total, pid)

    def _compute_noise_field(self, px, py):
        """Perlin noise field for liquid flow. Returns value in metaball-compatible range."""
        scale = self.params.get('noise_scale', 0.06)
        octaves = self.params.get('noise_octaves', 3)
        n = fbm3(px * scale, py * scale * 0.7, self._noise_time, octaves)
        # Map noise [-1,1] to field [0, ~6] so field_to_level works naturally
        # noise > 0 becomes lava, noise < 0 becomes liquid
        return max(0.0, (n + 0.3) * 5.0)

    # Trails: slow-shutter motion blur. When enabled, each cell records
    # the most recent lava level and fades over TRAIL_LIFE frames.
    TRAIL_LIFE = 14

    def _ensure_trail_buffer(self):
        """Allocate or resize the trail buffer to match body dimensions."""
        rows = self.body_height
        cols = self.body_width
        if (self.trail_buffer is None
                or len(self.trail_buffer) != rows
                or (rows and len(self.trail_buffer[0]) != cols)):
            self.trail_buffer = [
                [[0, 0, 0, 0, 0] for _ in range(cols)]
                for _ in range(rows)
            ]

    @staticmethod
    def _trail_decay_level(base_level, frames_left):
        """Map a remembered level + remaining life to a dimmed render level."""
        if base_level <= 0 or frames_left <= 0:
            return 0
        frac = frames_left / float(Lamp.TRAIL_LIFE)
        # Ease: long tail at low levels. 6 == rim (the soft glow color).
        if frac > 0.75:
            return min(base_level, 3)
        if frac > 0.5:
            return min(base_level, 2)
        if frac > 0.25:
            return min(base_level, 1)
        return 6  # rim/halo color for the last quarter of the tail

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

    def _get_forest_bg_color(self, px, py):
        """Returns ANSI color code for layered pine tree silhouette background, or None."""
        # Rolling ground hill at the bottom
        ground_y = self.phys_height - 1.5 - math.sin(px * 0.12) * 2.0
        if py > ground_y:
            # Warm campfire glow radiating from the fire center onto the ground
            cx = self.body_width / 2
            dist_norm = abs(px - cx) / max(1.0, self.body_width * 0.30)
            depth = (py - ground_y) / max(1.0, 2.5)
            warmth = max(0.0, (1.0 - dist_norm ** 1.2) * (1.0 - depth * 0.6))
            if warmth > 0.65:
                return 130   # warm orange-brown (firelit ground)
            elif warmth > 0.30:
                return 94    # darker brown
            return 232  # dark ground

        # Layered conifer silhouettes: (spacing, slope, height_var, base_y_off, color_main, color_edge)
        layers = [
            # Near (foreground) - Dark Green
            (32.0, 0.45, 20.0, -10.0, 22, 28),
            # Midground - Dark Grey
            (18.0, 0.32, 12.0, 5.0, 235, 236),
            # Distant - Almost Black
            (10.0, 0.22, 8.0, 15.0, 233, 234),
        ]

        for spacing, slope, h_var, y_off, c_main, c_edge in layers:
            # Deterministic local grid
            grid_x = int(px / spacing)
            for dx in (-1, 0, 1):
                idx = grid_x + dx
                # Simple hash for height and x-offset
                h = (idx * 17 ^ idx * 31) % 100 / 100.0
                tree_x = (idx + 0.5 + (h - 0.5) * 0.6) * spacing
                tree_top_y = y_off + (1.0 - h) * h_var
                
                if py > tree_top_y:
                    dy = py - tree_top_y
                    # Conifer shape: triangular branches with jagged edges
                    # Branch layers using a sine wave modifier on width
                    jagged = math.sin(dy * 1.6) * 1.5 + math.sin(dy * 3.5) * 0.5
                    width = dy * slope + jagged
                    
                    dist_to_center = abs(px - tree_x)
                    if dist_to_center < width:
                        # Edge highlight for pixel-art depth
                        if dist_to_center > width - 1.2:
                            return c_edge
                        return c_main

        # Night sky stars (sparse hash)
        star_h = (int(px) * 73 ^ int(py) * 97) % 1200
        if star_h == 0 and py < self.phys_height * 0.5:
            return 250  # Bright star
        elif star_h == 1 and py < self.phys_height * 0.7:
            return 241  # Dim star
            
        return None

    def _get_campfire_log_color(self, px, py):
        """Returns ANSI color code for pixel-art campfire logs, or None if no log/ember."""
        cx = self.body_width / 2
        bot = self.phys_height - 0.5
        # Scale campfire structure to terminal width
        L = min(28.0, self.body_width * 0.6)
        if py < bot - L:
            return None

        # x1, y1, x2, y2, radius (in physical half-block units)
        logs = [
            # Back upright log
            (cx + L * 0.1, bot + 2, cx - L * 0.2, bot - L * 0.8, L * 0.15),
            # Left leaning log
            (cx - L * 0.5, bot + 2, cx + L * 0.15, bot - L * 0.7, L * 0.18),
            # Right leaning log
            (cx + L * 0.5, bot + 1, cx - L * 0.1, bot - L * 0.75, L * 0.18),
            # Front horizontal log
            (cx - L * 0.4, bot, cx + L * 0.4, bot - L * 0.1, L * 0.22)
        ]

        best_z = -1
        best_c = None

        for i, (x1, y1, x2, y2, r) in enumerate(logs):
            dx = x2 - x1
            dy = y2 - y1
            l2 = dx * dx + dy * dy
            if l2 == 0: continue

            # Distance to line segment
            t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / l2))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            d = math.hypot(px - proj_x, py - proj_y)

            if d < r:
                # Z-order depth for layering
                z = i * 100 + (r - d)
                if z > best_z:
                    best_z = z
                    norm_d = d / r
                    # Wood ends (rings) at segments boundaries
                    if t < 0.05 or t > 0.95:
                        ring = int(norm_d * 5)
                        best_c = 137 if ring % 2 == 0 else 94
                    else:
                        # Bark texture (longitudinal stripes)
                        stripe = int((norm_d + t * 2.0) * 10) % 3
                        if norm_d < 0.4:
                            best_c = 130 if stripe == 0 else 94
                        elif norm_d < 0.7:
                            best_c = 94 if stripe == 0 else 52
                        else:
                            best_c = 52 if stripe == 0 else 234

                        # Glowing cracks and hot ash near bottom
                        if py > bot - L * 0.4:
                            crack = (int(px * 1.3) ^ int(py * 1.7)) % 7
                            if crack == 0 and norm_d > 0.5:
                                best_c = 202 if (int(px) ^ int(py)) % 2 == 0 else 196
                            elif crack == 1 and py > bot - L * 0.15:
                                best_c = 245  # Ash

        # Ember bed underneath everything
        if best_c is None and py > bot - L * 0.2:
            dx = (px - cx) / (L * 0.7)
            dy = (py - bot) / (L * 0.25)
            if dx * dx + dy * dy < 1.0:
                ember_noise = (int(px * 2.3) ^ int(py * 3.1)) % 5
                if ember_noise == 0: best_c = 196
                elif ember_noise == 1: best_c = 202
                elif ember_noise == 2: best_c = 52
                else: best_c = 232

        return best_c

    def _get_xmas_bg_color(self, px, py):
        """Indoor Christmas fireplace: brick surround, wooden mantel, stockings, stone hearth."""
        w  = float(self.body_width)
        ph = float(self.phys_height)

        mantel_top = ph * 0.25
        mantel_bot = ph * 0.31
        fp_left    = w  * 0.10
        fp_right   = w  * 0.90
        open_left  = w  * 0.22
        open_right = w  * 0.78
        open_top   = mantel_bot
        lintel_h   = ph * 0.04
        hearth_top = ph * 0.88

        def brick(bx, by):
            row = int(by / 3)
            if int(by) % 3 == 0:
                return 236
            offset = 8 if row % 2 == 0 else 0
            if int(bx + offset) % 12 == 0:
                return 236
            shade = (int((bx + offset) / 12) + row) % 3
            return (88, 124, 52)[shade]

        # Wooden mantel shelf
        if mantel_top <= py < mantel_bot and fp_left <= px <= fp_right:
            t = (py - mantel_top) / (mantel_bot - mantel_top)
            return 137 if t < 0.2 else (94 if t < 0.65 else 58)

        # Christmas stockings hanging from the mantel
        leg_h  = ph * 0.13
        leg_w  = w  * 0.030
        cuff_h = ph * 0.022
        foot_h = ph * 0.028
        foot_w = w  * 0.048
        for sx, sc in ((w * 0.26, 160), (w * 0.74, 196)):
            body_bot = mantel_bot + leg_h
            if py < mantel_bot or py > body_bot + foot_h:
                continue
            foot_dir = 1 if sx < w * 0.5 else -1
            foot_cx  = sx + foot_dir * foot_w * 0.55
            if abs(px - sx) < leg_w:
                if py < mantel_bot + cuff_h:
                    return 231   # white cuff
                if py < body_bot:
                    return sc    # stocking body
            if body_bot - foot_h * 0.5 <= py <= body_bot + foot_h and abs(px - foot_cx) < foot_w:
                return sc        # stocking foot

        # Brick left pillar
        if fp_left <= px < open_left and open_top <= py < hearth_top:
            return brick(px, py)

        # Brick right pillar
        if open_right < px <= fp_right and open_top <= py < hearth_top:
            return brick(px, py)

        # Brick lintel above the opening
        if open_left <= px <= open_right and open_top <= py < open_top + lintel_h:
            return brick(px, py)

        # Multi-tongue procedural hearth flame
        if open_left <= px <= open_right and open_top + lintel_h <= py < hearth_top:
            h_range = hearth_top - (open_top + lintel_h)
            # h_base: 0 = hearth (flame base), 1 = top of opening (flame tips)
            h_base = 1.0 - (py - (open_top + lintel_h)) / h_range

            cx_open = (open_left + open_right) * 0.5
            half_w  = (open_right - open_left) * 0.5

            t = self._noise_time

            # Size multipliers: 0=small/cozy, 1=medium, 2=large/roaring
            H_MULT = (0.52, 0.80, 1.05)[self.flame_size]
            W_MULT = (0.58, 0.80, 1.00)[self.flame_size]

            # Whole flame sways left/right together
            sway = math.sin(t * 1.4) * 0.07

            # Tongue params: (x_frac_of_half_w, tip_height_frac, base_width_frac)
            # tip_height_frac: how high above the base the tongue tip reaches (fraction of opening)
            tongues = (
                (sway,               1.00 * H_MULT, 0.64 * W_MULT),  # center — tallest
                (-0.28 + sway * 0.5, 0.72 * H_MULT, 0.36 * W_MULT),  # left
                ( 0.30 + sway * 0.5, 0.68 * H_MULT, 0.34 * W_MULT),  # right
            )

            best_heat = 0.0
            for xf, tip_h, wf in tongues:
                if h_base > tip_h:
                    continue                          # above this tongue's tip
                # rel_h: 0 = tongue tip (top), 1 = flame base (bottom/hearth)
                rel_h = 1.0 - h_base / tip_h
                tongue_cx = cx_open + xf * half_w
                tongue_w  = wf * half_w * (rel_h ** 0.5)  # wide at base, narrows upward
                # Organic edge turbulence
                turb = math.sin(t * 3.8 + py * 0.18 + xf * 4.0) * 0.06 * tongue_w
                tongue_w = max(0.0, tongue_w + turb)
                dx_t = abs(px - tongue_cx)
                if dx_t < tongue_w:
                    intensity = (tongue_w - dx_t) / max(0.01, tongue_w)
                    heat = intensity * (0.30 + 0.70 * rel_h)  # hotter at base
                    if heat > best_heat:
                        best_heat = heat

            # black → dark-red → red → orange → gold → white-hot
            FLAME = (16, 52, 88, 124, 160, 196, 202, 208, 214, 220, 226, 231)
            if best_heat > 0.0:
                return FLAME[min(len(FLAME) - 1, int(best_heat * len(FLAME)))]
            return 16   # dark backdrop between / above tongues

        # Stone hearth
        if hearth_top <= py and fp_left - w * 0.05 <= px <= fp_right + w * 0.05:
            stone = (int(px / 7) ^ int((py - hearth_top) / 2)) % 3
            return 240 if stone == 0 else (244 if stone == 1 else 237)

        # Hardwood floor planks
        if py >= ph * 0.94:
            return 94 if int(px / 14) % 2 == 0 else 130

        # Room wall (dark warm gray)
        return 235

    def render_freestyle(self, screen, x_off, y_off, ch):
        """Render fullscreen lava with no lamp frame."""
        if self.trails:
            self._ensure_trail_buffer()
        for row in range(self.body_height):
            py_t = row * 2
            py_b = row * 2 + 1
            sy = y_off + row
            for col in range(self.body_width):
                px = col + 0.5
                if self.bicolor:
                    ft, t_pid = self.compute_field_bicolor(px, py_t + 0.5)
                    fb, b_pid = self.compute_field_bicolor(px, py_b + 0.5)
                else:
                    ft = self.compute_field(px, py_t + 0.5)
                    fb = self.compute_field(px, py_b + 0.5)
                    t_pid = b_pid = 0
                tl = self.field_to_level(ft)
                bl = self.field_to_level(fb)

                # Procedural campfire composite (fireplace/campfire style, or fireplace+campfire theme)
                if self.style in ('fireplace', 'campfire') and ch._has_256:
                    t_bg = None
                    b_bg = None
                    if self.style == 'campfire' or ch.theme_name == 'campfire':
                        t_bg = self._get_forest_bg_color(px, py_t + 0.5)
                        b_bg = self._get_forest_bg_color(px, py_b + 0.5)

                    t_log = self._get_campfire_log_color(px, py_t + 0.5)
                    b_log = self._get_campfire_log_color(px, py_b + 0.5)

                    if t_log is not None or b_log is not None or t_bg is not None or b_bg is not None:
                        # Composite Layering: Background -> Lava/Embers -> Logs
                        tc = ch._color_for_level(tl, t_pid)
                        bc = ch._color_for_level(bl, b_pid)

                        # If cell half is empty liquid, show forest background
                        if tl == 0 and t_bg is not None: tc = t_bg
                        if bl == 0 and b_bg is not None: bc = b_bg

                        # Logs always on top
                        if t_log is not None: tc = t_log
                        if b_log is not None: bc = b_log

                        ch.draw_colored_cell(screen, sy, x_off + col, tc, bc)
                        continue

                elif self.style == 'xmas' and ch._has_256:
                    # Pure procedural scene — no blobs, draw background directly
                    tc = self._get_xmas_bg_color(px, py_t + 0.5) or 235
                    bc = self._get_xmas_bg_color(px, py_b + 0.5) or 235
                    ch.draw_colored_cell(screen, sy, x_off + col, tc, bc)
                    continue

                if self.trails:
                    entry = self.trail_buffer[row][col]
                    has_lava = tl > 0 or bl > 0
                    if has_lava:
                        # Refresh the trail memory with the live cell
                        entry[0] = tl
                        entry[1] = bl
                        entry[2] = self.TRAIL_LIFE
                        entry[3] = t_pid
                        entry[4] = b_pid
                    elif entry[2] > 0:
                        # Liquid now, but paint a fading ghost of the past
                        gtl = self._trail_decay_level(entry[0], entry[2])
                        gbl = self._trail_decay_level(entry[1], entry[2])
                        entry[2] -= 1
                        if gtl > 0 or gbl > 0:
                            ch.draw_cell(screen, sy, x_off + col,
                                         gtl, gbl, entry[3], entry[4])
                            continue
                ch.draw_cell(screen, sy, x_off + col, tl, bl, t_pid, b_pid)

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

            # -- Glass frame outline: left and right border columns --
            # Rocket lamps use chrome (bright metal) framing so the
            # body reads as a single chrome rocket; other styles use
            # the dark glass-bead outline.
            py_t, py_b = row * 2, row * 2 + 1
            lt, rt = self.get_body_bounds(py_t)
            lb, rb = self.get_body_bounds(py_b)
            ol_px = outer_left + 0.5
            or_px = outer_right + 0.5
            l_top_in = lt <= ol_px <= rt
            l_bot_in = lb <= ol_px <= rb
            r_top_in = lt <= or_px <= rt
            r_bot_in = lb <= or_px <= rb
            if self.style == 'rocket':
                ch.draw_base_cell(screen, sy, bx + outer_left,
                                  l_top_in, l_bot_in, shade='hi')
                ch.draw_base_cell(screen, sy, bx + outer_right,
                                  r_top_in, r_bot_in, shade='hi')
            else:
                ch.draw_frame_cell(screen, sy, bx + outer_left,
                                   l_top_in, l_bot_in)
                ch.draw_frame_cell(screen, sy, bx + outer_right,
                                   r_top_in, r_bot_in)

            # -- Glass interior: liquid background + lava metaballs --
            if self.trails:
                self._ensure_trail_buffer()
            # Glass bounds depend only on row; compute once per row.
            glt, grt = self.get_glass_bounds(py_t)
            glb, grb = self.get_glass_bounds(py_b)
            for col in range(inner_left, inner_right + 1):
                px = col + 0.5
                top_in = glt <= px <= grt
                bot_in = glb <= px <= grb

                if self.bicolor:
                    if top_in:
                        ft, t_pid = self.compute_field_bicolor(px, py_t + 0.5)
                    else:
                        ft, t_pid = 0, 0
                    if bot_in:
                        fb, b_pid = self.compute_field_bicolor(px, py_b + 0.5)
                    else:
                        fb, b_pid = 0, 0
                else:
                    ft = self.compute_field(px, py_t + 0.5) if top_in else 0
                    fb = self.compute_field(px, py_b + 0.5) if bot_in else 0
                    t_pid = b_pid = 0

                tl = self.field_to_level(ft) if top_in else -1
                bl = self.field_to_level(fb) if bot_in else -1

                if self.trails and 0 <= row < len(self.trail_buffer) \
                        and 0 <= col < len(self.trail_buffer[row]):
                    entry = self.trail_buffer[row][col]
                    has_lava = (tl > 0) or (bl > 0)
                    if has_lava:
                        entry[0] = tl if tl > 0 else 0
                        entry[1] = bl if bl > 0 else 0
                        entry[2] = self.TRAIL_LIFE
                        entry[3] = t_pid
                        entry[4] = b_pid
                    elif entry[2] > 0:
                        gtl = self._trail_decay_level(entry[0], entry[2])
                        gbl = self._trail_decay_level(entry[1], entry[2])
                        entry[2] -= 1
                        # Only paint the ghost inside glass
                        if (gtl > 0 or gbl > 0) and (top_in or bot_in):
                            draw_tl = gtl if top_in else -1
                            draw_bl = gbl if bot_in else -1
                            ch.draw_cell(screen, sy, bx + col,
                                         draw_tl, draw_bl, entry[3], entry[4])
                            continue

                ch.draw_cell(screen, sy, bx + col, tl, bl, t_pid, b_pid)

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

            # Cap shape and half-row widths depend only on row; hoist them.
            py_t = row * 2
            py_b = row * 2 + 1
            _cp = self._get_cap_profile()
            _denom = max(1, self.cap_height * 2)
            cap_w_t = _interpolate_profile(_cp, py_t / _denom) * body_top_w
            cap_w_b = _interpolate_profile(_cp, py_b / _denom) * body_top_w
            half_t = cap_w_t / 2
            half_b = cap_w_b / 2
            center = body_top_w / 2

            for col in range(left, right + 1):
                px = col - top_left + 0.5
                t_in = (center - half_t) <= px <= (center + half_t)
                b_in = (center - half_b) <= px <= (center + half_b)

                # 3-tone shading: bright at dome peak, mid in body, shadow at base
                if norm_y < 0.3:
                    shade = 'hi'
                elif norm_y < 0.7:
                    shade = 'mid'
                else:
                    shade = 'sh'
                # Rocket: blend in a horizontal chrome stripe so the
                # nose cone reads as polished metal, not flat plastic.
                if self.style == 'rocket':
                    # col is in absolute body-grid coords; use absolute
                    # body_width as the reference span
                    shade = self._chrome_shade(col, self.body_width,
                                               norm_y, shade)
                ch.draw_base_cell(screen, sy, bx + col, t_in, b_in, shade=shade)

    def _render_base(self, screen, bx, base_y, bot_bounds, ch):
        """Render the metallic tapered pedestal below the glass body."""
        bot_left, bot_right = bot_bounds
        body_bot_w = bot_right - bot_left + 1

        for row in range(self.base_height):
            norm_y = row / max(1, self.base_height - 1) if self.base_height > 1 else 1.0
            bl, br = self._base_bounds_at(norm_y, body_bot_w)

            # bl, br are already in absolute body-grid coords (centered at body_width/2)
            left = int(math.ceil(bl))
            right = int(math.floor(br)) - 1
            left = max(0, left)
            right = min(self.body_width - 1, right)
            sy = base_y + row

            # Base shape and half-row widths depend only on row; hoist them.
            py_t = row * 2
            py_b = row * 2 + 1
            _bp = self._get_base_profile()
            ref_w = self.body_width if self.style == 'rocket' else body_bot_w
            _denom = max(1, self.base_height * 2)
            bw_t = _interpolate_profile(_bp, py_t / _denom) * ref_w
            bw_b = _interpolate_profile(_bp, py_b / _denom) * ref_w
            half_t = bw_t / 2
            half_b = bw_b / 2
            cx = self.body_width / 2

            for col in range(left, right + 1):
                px = col + 0.5  # absolute body-grid position
                t_in = (cx - half_t) <= px <= (cx + half_t)
                b_in = (cx - half_b) <= px <= (cx + half_b)

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
                # Rocket: overlay the chrome curvature stripe so the
                # fins and stem read as polished metal.
                if self.style == 'rocket':
                    shade = self._chrome_shade(col, self.body_width,
                                               norm_y, shade)
                ch.draw_base_cell(screen, sy, bx + col, t_in, b_in, shade=shade)

    # ----- Controls -----

    def add_ball(self):
        y = random.uniform(self.phys_height * 0.6, self.phys_height * 0.9)
        gl, gr = self.get_glass_bounds(y)
        x = random.uniform(gl + 0.5, gr - 0.5)
        # Keep bicolor balanced: add to the minority palette
        if self.bicolor:
            count_b = sum(1 for b in self.balls if b.palette_id == 1)
            count_a = len(self.balls) - count_b
            pid = 1 if count_b <= count_a else 0
        else:
            pid = 0
        self.balls.append(Ball(x, y, self.ball_radius, palette_id=pid))

    def remove_ball(self):
        if len(self.balls) > 1:
            # Bicolor: remove from the majority palette to keep balance
            if self.bicolor:
                count_b = sum(1 for b in self.balls if b.palette_id == 1)
                count_a = len(self.balls) - count_b
                target_pid = 1 if count_b > count_a else 0
                for i in range(len(self.balls) - 1, -1, -1):
                    if self.balls[i].palette_id == target_pid:
                        self.balls.pop(i)
                        return
            self.balls.pop()

    def resize(self, new_width, new_height, new_base_h, new_cap_h, new_ball_r=None):
        """Resize the lamp, repositioning balls proportionally."""
        old_w, old_ph = self.body_width, self.phys_height
        self.body_width = new_width
        self.body_height = new_height
        self.phys_height = new_height * 2
        self.base_height = new_base_h
        self.cap_height = new_cap_h

        # Scale ball radius to match new dimensions
        if new_ball_r is not None:
            self.ball_radius = new_ball_r
        elif old_w > 0:
            self.ball_radius *= new_width / old_w

        for ball in self.balls:
            ball.x = ball.x * new_width / old_w if old_w > 0 else new_width / 2
            ball.y = ball.y * self.phys_height / old_ph if old_ph > 0 else self.phys_height / 2
        # Trail buffer dims no longer match; force reallocation next frame
        self.trail_buffer = None
