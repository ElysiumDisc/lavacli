"""Koi pond simulation with skeletal fish and half-block rendering."""
import math
import random

# ---------------------------------------------------------------------------
# Fish body profile — much larger, properly fish-shaped
# Each value is the half-width at that segment (in physical half-block cells)
# ---------------------------------------------------------------------------
#   0    1    2    3    4    5    6    7    8    9   10   11   12   13
# head  neck  ---- body (widest) ----  taper  peduncle  -- tail fin --
BODY_WIDTHS = [
    0.6,   # 0: snout tip (pointed)
    1.4,   # 1: head
    2.6,   # 2: gill/neck
    3.8,   # 3: shoulder
    4.8,   # 4: pectoral (widest, fins here)
    5.2,   # 5: belly (widest)
    5.0,   # 6: mid-body
    4.4,   # 7: body taper
    3.4,   # 8: rear body
    2.2,   # 9: taper
    1.2,   # 10: caudal peduncle (narrow)
    0.8,   # 11: peduncle base
    2.4,   # 12: tail fin spread
    3.6,   # 13: tail fin tips (fans out)
]
NUM_SEGMENTS = len(BODY_WIDTHS)
SEGMENT_LENGTH = 3.2     # distance between segments in physical units
FIN_SEGMENTS = {4, 5}    # pectoral fin segments
FIN_EXTENSION = 3.0      # extra width for pectoral fins
SWIM_PERIOD = 48          # frames per sinusoidal cycle
SWIM_AMPLITUDE = 0.4     # lateral displacement amplitude


class Segment:
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Fish:
    """A single koi fish made of connected segments."""

    def __init__(self, x, y, pond_w, pond_h, color_pattern):
        self.segments = []
        for i in range(NUM_SEGMENTS):
            self.segments.append(Segment(x - i * SEGMENT_LENGTH, y))
        margin = max(10, min(pond_w, pond_h) * 0.1)
        self.target_x = random.uniform(margin, pond_w - margin)
        self.target_y = random.uniform(margin, pond_h - margin)
        self.speed = random.uniform(0.4, 0.7)
        self.phase = random.uniform(0, 2 * math.pi)
        self.frame = 0
        self.color_pattern = color_pattern
        self.pond_w = pond_w
        self.pond_h = pond_h

    def update(self, speed_mult=1.0):
        self.frame += 1
        head = self.segments[0]

        # Direction to target
        dx = self.target_x - head.x
        dy = self.target_y - head.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 5.0:
            margin = max(10, min(self.pond_w, self.pond_h) * 0.1)
            self.target_x = random.uniform(margin, self.pond_w - margin)
            self.target_y = random.uniform(margin, self.pond_h - margin)
            dx = self.target_x - head.x
            dy = self.target_y - head.y
            dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0.01:
            nx, ny = dx / dist, dy / dist
        else:
            nx, ny = 1.0, 0.0

        # Perpendicular for sinusoidal swimming undulation
        perp_x, perp_y = -ny, nx
        # Amplitude increases toward tail via segment constraints,
        # but head gets a subtle wobble too
        sin_offset = (math.sin(self.frame * 2 * math.pi / SWIM_PERIOD + self.phase)
                      * SWIM_AMPLITUDE)

        # Move head
        effective_speed = self.speed * speed_mult
        head.x += (nx + perp_x * sin_offset) * effective_speed
        head.y += (ny + perp_y * sin_offset) * effective_speed

        # Boundary avoidance: gentle steering force near edges
        margin = max(8, min(self.pond_w, self.pond_h) * 0.08)
        steer = 0.5
        if head.x < margin:
            head.x += steer
        elif head.x > self.pond_w - margin:
            head.x -= steer
        if head.y < margin:
            head.y += steer
        elif head.y > self.pond_h - margin:
            head.y -= steer

        # Clamp
        head.x = max(1, min(self.pond_w - 2, head.x))
        head.y = max(1, min(self.pond_h - 2, head.y))

        # Constrain subsequent segments (pull toward predecessor)
        for i in range(1, len(self.segments)):
            seg = self.segments[i]
            prev = self.segments[i - 1]
            sdx = seg.x - prev.x
            sdy = seg.y - prev.y
            d = math.sqrt(sdx * sdx + sdy * sdy)
            if d > SEGMENT_LENGTH:
                ratio = SEGMENT_LENGTH / d
                seg.x = prev.x + sdx * ratio
                seg.y = prev.y + sdy * ratio


class Pond:
    """Fullscreen koi pond with multiple colored fish."""

    def __init__(self, width, height, fish_count, speed_mult=1.0):
        self.width = width
        self.height = height
        self.phys_h = height * 2
        self.speed_mult = speed_mult
        self.paused = False
        self.fish_list = []
        self._init_fish(fish_count)

    def _init_fish(self, count):
        from .themes import KOI_PATTERN_NAMES
        for i in range(count):
            # Spread fish out across the pond
            x = random.uniform(15, max(16, self.width - 15))
            y = random.uniform(15, max(16, self.phys_h - 15))
            pattern = KOI_PATTERN_NAMES[i % len(KOI_PATTERN_NAMES)]
            self.fish_list.append(Fish(x, y, self.width, self.phys_h, pattern))

    def update(self):
        if self.paused:
            return
        for fish in self.fish_list:
            fish.update(self.speed_mult)

    def render(self, screen, ch):
        """Render the pond using a buffer + half-block output."""
        w, ph = self.width, self.phys_h
        # Build buffer: None = water, (pattern, seg_idx, dist) = fish
        buffer = [[None] * w for _ in range(ph)]

        for fish in self.fish_list:
            self._stamp_fish(buffer, fish, w, ph)

        # Draw half-block pairs
        for row in range(self.height):
            py_t = row * 2
            py_b = row * 2 + 1
            for col in range(w):
                top = buffer[py_t][col] if py_t < ph else None
                bot = buffer[py_b][col] if py_b < ph else None
                ch.draw_pond_cell(screen, row, col, top, bot)

    def _stamp_fish(self, buffer, fish, w, ph):
        """Rasterize a fish body into the buffer with proper fish shape."""
        segs = fish.segments
        n = len(segs)
        pattern = fish.color_pattern

        for i in range(n):
            seg = segs[i]
            body_w = BODY_WIDTHS[i] if i < len(BODY_WIDTHS) else 0.5

            # Compute local direction for perpendicular
            if i == 0 and n > 1:
                fdx = seg.x - segs[1].x
                fdy = seg.y - segs[1].y
            elif i < n - 1:
                fdx = segs[i + 1].x - seg.x
                fdy = segs[i + 1].y - seg.y
            else:
                fdx = seg.x - segs[i - 1].x
                fdy = seg.y - segs[i - 1].y
            length = math.sqrt(fdx * fdx + fdy * fdy)
            if length > 0.01:
                perp_x, perp_y = -fdy / length, fdx / length
            else:
                perp_x, perp_y = 0.0, 1.0

            # Fill cells along perpendicular width
            self._fill_width(buffer, seg.x, seg.y, perp_x, perp_y,
                             body_w, pattern, i, w, ph)

            # Pectoral fins: extra triangular extension
            if i in FIN_SEGMENTS:
                fin_w = body_w + FIN_EXTENSION
                # Only fill the outer fin region (beyond body edge)
                self._fill_fin(buffer, seg.x, seg.y, perp_x, perp_y,
                               body_w, fin_w, pattern, i, w, ph)

            # Interpolate between this segment and next for smooth body
            if i < n - 1:
                nxt = segs[i + 1]
                next_w = BODY_WIDTHS[i + 1] if i + 1 < len(BODY_WIDTHS) else 0.5
                sdx = nxt.x - seg.x
                sdy = nxt.y - seg.y
                seg_dist = math.sqrt(sdx * sdx + sdy * sdy)
                interp_steps = max(3, int(seg_dist * 1.2))

                for t in range(1, interp_steps):
                    frac = t / interp_steps
                    mx = seg.x + sdx * frac
                    my = seg.y + sdy * frac
                    interp_w = body_w + (next_w - body_w) * frac
                    seg_idx = i if frac < 0.5 else i + 1
                    self._fill_width(buffer, mx, my, perp_x, perp_y,
                                     interp_w, pattern, seg_idx, w, ph)

    def _fill_width(self, buffer, cx, cy, perp_x, perp_y,
                    half_width, pattern, seg_idx, w, ph):
        """Fill cells perpendicular to spine at (cx, cy)."""
        steps = max(1, int(half_width * 2.5 + 1))
        for s in range(-steps, steps + 1):
            frac = s / max(1, steps)
            px = int(cx + perp_x * half_width * frac + 0.5)
            py = int(cy + perp_y * half_width * frac + 0.5)
            if 0 <= px < w and 0 <= py < ph:
                dist = abs(frac)
                existing = buffer[py][px]
                if existing is None or dist < existing[2]:
                    buffer[py][px] = (pattern, seg_idx, dist)

    def _fill_fin(self, buffer, cx, cy, perp_x, perp_y,
                  inner_w, outer_w, pattern, seg_idx, w, ph):
        """Fill the fin region between inner_w and outer_w."""
        steps = max(1, int(outer_w * 2.5 + 1))
        for s in range(-steps, steps + 1):
            frac = s / max(1, steps)
            abs_frac = abs(frac)
            # Only fill outside the main body
            if abs_frac * outer_w < inner_w:
                continue
            px = int(cx + perp_x * outer_w * frac + 0.5)
            py = int(cy + perp_y * outer_w * frac + 0.5)
            if 0 <= px < w and 0 <= py < ph:
                existing = buffer[py][px]
                # Fins are always outer (dist > 0.6) so color resolves to fin
                if existing is None:
                    buffer[py][px] = (pattern, seg_idx, 0.8)

    def resize(self, new_width, new_height):
        old_w, old_ph = self.width, self.phys_h
        self.width = new_width
        self.height = new_height
        self.phys_h = new_height * 2
        for fish in self.fish_list:
            for seg in fish.segments:
                seg.x = seg.x * new_width / old_w if old_w > 0 else new_width / 2
                seg.y = seg.y * self.phys_h / old_ph if old_ph > 0 else self.phys_h / 2
            fish.pond_w = new_width
            fish.pond_h = self.phys_h
            fish.target_x = max(10, min(fish.target_x * new_width / old_w,
                                        new_width - 10))
            fish.target_y = max(10, min(fish.target_y * self.phys_h / old_ph,
                                        self.phys_h - 10))

    def add_fish(self):
        from .themes import KOI_PATTERN_NAMES
        x = random.uniform(15, max(16, self.width - 15))
        y = random.uniform(15, max(16, self.phys_h - 15))
        pattern = random.choice(KOI_PATTERN_NAMES)
        self.fish_list.append(Fish(x, y, self.width, self.phys_h, pattern))

    def remove_fish(self):
        if len(self.fish_list) > 1:
            self.fish_list.pop()
