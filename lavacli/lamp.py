"""Lava lamp simulation with metaball physics and half-block rendering."""
import curses
import math
import random

# Shape profiles: (normalized_y, normalized_width) pairs
# y: 0=top, 1=bottom  |  width: 0=zero, 1=max
SHAPES = {
    'classic': [
        (0.00, 0.28), (0.04, 0.34), (0.10, 0.52), (0.16, 0.70),
        (0.22, 0.84), (0.30, 0.94), (0.40, 1.00), (0.50, 1.00),
        (0.60, 0.97), (0.70, 0.92), (0.80, 0.85), (0.90, 0.80),
        (1.00, 0.76),
    ],
    'slim': [
        (0.00, 0.40), (0.06, 0.48), (0.12, 0.58), (0.20, 0.65),
        (0.30, 0.70), (0.50, 0.72), (0.70, 0.70), (0.80, 0.65),
        (0.90, 0.58), (1.00, 0.50),
    ],
    'globe': [
        (0.00, 0.15), (0.05, 0.35), (0.12, 0.60), (0.20, 0.80),
        (0.30, 0.94), (0.40, 1.00), (0.50, 1.00), (0.60, 0.94),
        (0.70, 0.80), (0.80, 0.60), (0.88, 0.40), (1.00, 0.25),
    ],
    'lava': [
        (0.00, 0.22), (0.06, 0.40), (0.12, 0.60), (0.20, 0.80),
        (0.26, 0.92), (0.32, 1.00), (0.38, 0.96), (0.44, 0.90),
        (0.50, 0.94), (0.56, 1.00), (0.64, 0.97), (0.72, 0.92),
        (0.80, 0.86), (0.90, 0.78), (1.00, 0.70),
    ],
    'diamond': [
        (0.00, 0.20), (0.10, 0.35), (0.20, 0.55), (0.30, 0.75),
        (0.40, 0.90), (0.50, 1.00), (0.60, 0.90), (0.70, 0.75),
        (0.80, 0.55), (0.90, 0.35), (1.00, 0.20),
    ],
}

SHAPE_ORDER = ['classic', 'slim', 'globe', 'lava', 'diamond']

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

SIZE_DEFAULTS = {
    'S': {'body_height': 14, 'body_width': 10, 'num_balls': 3, 'ball_radius': 2.0},
    'M': {'body_height': 22, 'body_width': 14, 'num_balls': 5, 'ball_radius': 2.8},
    'L': {'body_height': 32, 'body_width': 18, 'num_balls': 7, 'ball_radius': 3.5},
}

SIZE_ORDER = ['S', 'M', 'L']
SIZE_NAMES = {'S': 'Small', 'M': 'Medium', 'L': 'Large'}


class Ball:
    __slots__ = ('x', 'y', 'vx', 'vy', 'radius', 'temp')

    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.2, 0.2)
        self.vy = random.uniform(-0.1, 0.1)
        self.radius = radius
        self.temp = random.uniform(0.2, 0.5)


class Lamp:
    CAP_HEIGHT = 2
    BASE_HEIGHT = 2

    def __init__(self, style, body_width, body_height, flow_type, num_balls, ball_radius):
        self.style = style
        self.body_width = body_width
        self.body_height = body_height
        self.phys_height = body_height * 2
        self.flow_type = flow_type
        self.params = FLOW_PARAMS[flow_type]
        self.profile = SHAPES[style]
        self.ball_radius = ball_radius
        self.speed_mult = 1.0
        self.paused = False
        self._screen_bounds_cache = None

        self.balls = []
        for _ in range(num_balls):
            x = random.uniform(self.body_width * 0.3, self.body_width * 0.7)
            y = random.uniform(self.phys_height * 0.6, self.phys_height * 0.9)
            self.balls.append(Ball(x, y, ball_radius))

    @property
    def total_width(self):
        return self.body_width + 4  # 2 border + 2 padding

    @property
    def total_height(self):
        return self.body_height + self.CAP_HEIGHT + self.BASE_HEIGHT

    def get_width_at(self, norm_y):
        """Interpolate profile to get width ratio (0-1) at normalized y (0-1)."""
        norm_y = max(0.0, min(1.0, norm_y))
        profile = self.profile
        if norm_y <= profile[0][0]:
            return profile[0][1]
        if norm_y >= profile[-1][0]:
            return profile[-1][1]
        for i in range(len(profile) - 1):
            y0, w0 = profile[i]
            y1, w1 = profile[i + 1]
            if y0 <= norm_y <= y1:
                t = (norm_y - y0) / (y1 - y0) if y1 != y0 else 0
                # Smooth interpolation (cubic hermite for smoother curves)
                t = t * t * (3 - 2 * t)
                return w0 + t * (w1 - w0)
        return profile[-1][1]

    def get_bounds(self, phys_y):
        """Get (left, right) x bounds at physical y coordinate."""
        norm_y = phys_y / self.phys_height
        width_ratio = self.get_width_at(norm_y)
        half_w = width_ratio * self.body_width / 2
        center = self.body_width / 2
        return (center - half_w, center + half_w)

    def compute_screen_bounds(self):
        """Get integer column bounds for each body row."""
        bounds = []
        for row in range(self.body_height):
            phys_y_top = row * 2
            phys_y_bot = row * 2 + 1
            lt, rt = self.get_bounds(phys_y_top)
            lb, rb = self.get_bounds(phys_y_bot)
            left = int(math.ceil(min(lt, lb)))
            right = int(math.floor(max(rt, rb))) - 1
            left = max(0, left)
            right = min(self.body_width - 1, right)
            bounds.append((left, right))

        # Smooth: adjacent rows differ by at most 1 column
        for i in range(1, len(bounds)):
            l, r = bounds[i]
            pl, pr = bounds[i - 1]
            l = max(l, pl - 1)
            l = min(l, pl + 1)
            r = min(r, pr + 1)
            r = max(r, pr - 1)
            if r < l:
                mid = (l + r) // 2
                l = mid
                r = mid
            bounds[i] = (l, r)

        self._screen_bounds_cache = bounds
        return bounds

    def update(self):
        """Advance physics by one step."""
        if self.paused:
            return

        p = self.params
        sm = self.speed_mult

        for ball in self.balls:
            # Gravity
            ball.vy += p['gravity'] * sm

            # Temperature-based buoyancy
            ball.vy -= p['buoyancy'] * ball.temp * sm

            # Temperature dynamics
            norm_y = ball.y / self.phys_height
            if norm_y > 0.75:
                ball.temp = min(1.0, ball.temp + p['heat_rate'] * sm)
            elif norm_y < 0.25:
                ball.temp = max(0.0, ball.temp - p['cool_rate'] * sm)
            else:
                ball.temp = max(0.0, ball.temp - p['cool_rate'] * 0.3 * sm)

            # Random perturbation
            ball.vx += random.gauss(0, p['random_force']) * sm
            ball.vy += random.gauss(0, p['random_force'] * 0.5) * sm

            # Swirl force (circular around center)
            if p['swirl'] > 0:
                cx = self.body_width / 2
                cy = self.phys_height / 2
                dx = ball.x - cx
                dy = ball.y - cy
                ball.vx += -dy * p['swirl'] * sm
                ball.vy += dx * p['swirl'] * sm

            # Damping
            ball.vx *= p['damping']
            ball.vy *= p['damping']

            # Move
            ball.x += ball.vx * sm
            ball.y += ball.vy * sm

            # Wall collisions
            left, right = self.get_bounds(ball.y)
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

    def compute_field(self, px, py):
        """Compute metaball field strength at (px, py)."""
        total = 0.0
        for ball in self.balls:
            dx = px - ball.x
            dy = (py - ball.y) * 0.5  # squash vertically for wider blobs
            d_sq = dx * dx + dy * dy
            if d_sq < 0.001:
                d_sq = 0.001
            total += (ball.radius * ball.radius) / d_sq
        return total

    @staticmethod
    def field_to_level(field):
        """Convert field strength to lava intensity level (0=glass, 1-5=lava)."""
        if field < 1.0:
            return 0
        elif field < 1.6:
            return 1
        elif field < 2.4:
            return 2
        elif field < 3.5:
            return 3
        elif field < 5.0:
            return 4
        else:
            return 5

    def render(self, screen, x_off, y_off, ch):
        """Render the complete lamp at screen position (x_off, y_off).
        ch: ColorHelper instance."""
        bounds = self.compute_screen_bounds()
        body_x = x_off + 2  # offset for border columns
        body_y = y_off + self.CAP_HEIGHT

        # Render lava inside the body
        for row in range(self.body_height):
            left_col, right_col = bounds[row]
            sy = body_y + row

            for col in range(left_col, right_col + 1):
                sx = body_x + col
                px = col + 0.5
                phys_y_top = row * 2
                phys_y_bot = row * 2 + 1

                lt, rt = self.get_bounds(phys_y_top)
                lb, rb = self.get_bounds(phys_y_bot)

                top_in = lt <= px <= rt
                bot_in = lb <= px <= rb

                ft = self.compute_field(px, phys_y_top + 0.5) if top_in else 0
                fb = self.compute_field(px, phys_y_bot + 0.5) if bot_in else 0

                tl = self.field_to_level(ft) if top_in else -1
                bl = self.field_to_level(fb) if bot_in else -1

                ch.draw_cell(screen, sy, sx, tl, bl)

        # Side borders (diagonal chars for curved shape)
        self._draw_border(screen, body_x, body_y, bounds, ch)

        # Cap includes top horizontal border
        self._draw_cap(screen, x_off, y_off, bounds[0], ch)

        # Base includes bottom horizontal border
        self._draw_base(screen, x_off, body_y + self.body_height, bounds[-1], ch)

    def _draw_border(self, screen, bx, by, bounds, ch):
        """Draw side borders with diagonal chars for the curved shape."""
        attr = ch.border_attr

        for row in range(self.body_height):
            left, right = bounds[row]
            bl = bx + left - 1
            br = bx + right + 1

            if row > 0:
                pl, pr = bounds[row - 1]
                pbl = bx + pl - 1
                pbr = bx + pr + 1

                # Diagonal chars based on expansion/contraction
                lchar = '\u2571' if bl < pbl else ('\u2572' if bl > pbl else '\u2502')
                rchar = '\u2572' if br > pbr else ('\u2571' if br < pbr else '\u2502')
            else:
                lchar = '\u2502'
                rchar = '\u2502'

            try:
                screen.addstr(by + row, bl, lchar, attr)
                screen.addstr(by + row, br, rchar, attr)
            except curses.error:
                pass

    def _draw_cap(self, screen, x_off, y_off, top_bounds, ch):
        """Draw the lamp cap and top horizontal border."""
        attr = ch.base_attr
        bx = x_off + 2
        center = bx + self.body_width // 2
        left, right = top_bounds
        bl = bx + left - 1
        br = bx + right + 1

        try:
            # Row 0: knob
            screen.addstr(y_off, center - 1, '\u256d\u2500\u256e', attr)

            # Row 1: top border connecting knob to body
            if br - bl >= 5:
                screen.addstr(y_off + 1, bl, '\u256d', attr)
                for c in range(bl + 1, center - 1):
                    screen.addstr(y_off + 1, c, '\u2500', attr)
                screen.addstr(y_off + 1, center - 1, '\u2518', attr)
                screen.addstr(y_off + 1, center, ' ', attr)
                screen.addstr(y_off + 1, center + 1, '\u2514', attr)
                for c in range(center + 2, br):
                    screen.addstr(y_off + 1, c, '\u2500', attr)
                screen.addstr(y_off + 1, br, '\u256e', attr)
            else:
                screen.addstr(y_off + 1, bl, '\u256d', attr)
                for c in range(bl + 1, br):
                    screen.addstr(y_off + 1, c, '\u2500', attr)
                screen.addstr(y_off + 1, br, '\u256e', attr)
        except curses.error:
            pass

    def _draw_base(self, screen, x_off, base_y, bot_bounds, ch):
        """Draw the lamp base and bottom horizontal border."""
        attr = ch.base_attr
        bx = x_off + 2
        center = bx + self.body_width // 2
        left, right = bot_bounds
        bl = bx + left - 1
        br = bx + right + 1

        try:
            # Row 0: bottom border connecting body to base
            if br - bl >= 5:
                screen.addstr(base_y, bl, '\u2570', attr)
                for c in range(bl + 1, center - 1):
                    screen.addstr(base_y, c, '\u2500', attr)
                screen.addstr(base_y, center - 1, '\u2510', attr)
                screen.addstr(base_y, center, ' ', attr)
                screen.addstr(base_y, center + 1, '\u250c', attr)
                for c in range(center + 2, br):
                    screen.addstr(base_y, c, '\u2500', attr)
                screen.addstr(base_y, br, '\u256f', attr)
            else:
                screen.addstr(base_y, bl, '\u2570', attr)
                for c in range(bl + 1, br):
                    screen.addstr(base_y, c, '\u2500', attr)
                screen.addstr(base_y, br, '\u256f', attr)

            # Row 1: pedestal
            screen.addstr(base_y + 1, center - 1, '\u2570\u2500\u256f', attr)
        except curses.error:
            pass

    def add_ball(self):
        """Add a new ball to the lamp."""
        x = random.uniform(self.body_width * 0.3, self.body_width * 0.7)
        y = random.uniform(self.phys_height * 0.6, self.phys_height * 0.9)
        self.balls.append(Ball(x, y, self.ball_radius))

    def remove_ball(self):
        """Remove a ball from the lamp."""
        if len(self.balls) > 1:
            self.balls.pop()

    def resize(self, new_width, new_height):
        """Resize the lamp, repositioning balls proportionally."""
        old_w = self.body_width
        old_ph = self.phys_height
        self.body_width = new_width
        self.body_height = new_height
        self.phys_height = new_height * 2
        self._screen_bounds_cache = None

        for ball in self.balls:
            ball.x = ball.x * new_width / old_w if old_w > 0 else new_width / 2
            ball.y = ball.y * self.phys_height / old_ph if old_ph > 0 else self.phys_height / 2
