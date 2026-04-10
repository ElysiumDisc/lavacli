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


class LilyPad:
    """A static elliptical lily pad with a characteristic V-notch.

    Coordinates are in physical half-block cells (same space as fish
    segments). The notch is rendered by skipping cells whose angle from
    the pad center falls inside a small wedge.
    """
    __slots__ = ('cx', 'cy', 'rx', 'ry', 'notch_angle', 'notch_half_width',
                 'shadow_offset')

    def __init__(self, cx, cy, rx, ry, notch_angle):
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry
        self.notch_angle = notch_angle
        self.notch_half_width = 0.32  # radians, ~18 degrees each side
        # Shadow patch sits slightly off-center for a hand-painted look
        self.shadow_offset = (random.uniform(-0.25, 0.25),
                              random.uniform(-0.25, 0.25))


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
        self.lily_pads = []
        self._init_fish(fish_count)
        self._init_lily_pads()

    def _init_fish(self, count):
        from .themes import KOI_PATTERN_NAMES
        # Bias toward kohaku/sanke (white-with-orange) so the pond
        # visually matches the watercolor reference image
        weighted = ['kohaku', 'kohaku', 'kohaku',
                    'sanke', 'sanke',
                    'tancho', 'ogon', 'asagi', 'showa']
        # Drop any weights for patterns that aren't actually defined
        weighted = [p for p in weighted if p in KOI_PATTERN_NAMES]
        for i in range(count):
            # Spread fish out across the pond
            x = random.uniform(15, max(16, self.width - 15))
            y = random.uniform(15, max(16, self.phys_h - 15))
            pattern = weighted[i % len(weighted)]
            self.fish_list.append(Fish(x, y, self.width, self.phys_h, pattern))

    def _init_lily_pads(self):
        """Scatter ~6-10 non-overlapping lily pads across the pond surface.

        Sized proportionally to the pond so they read at any terminal
        size. Uses simple Poisson-ish rejection sampling: keeps trying
        random positions until each new pad is far enough from existing
        ones (or until attempt budget runs out).
        """
        self.lily_pads = []
        if self.width < 20 or self.phys_h < 20:
            return  # too small for pads to look right

        # Pad count scales with area: ~1 pad per 1100 phys cells, clamped
        area = self.width * self.phys_h
        target = max(6, min(10, area // 1100))

        # Pad size scales with the pond's smaller dimension so they
        # don't dominate tiny terminals
        smin = min(self.width, self.phys_h)
        rx_min = max(4, smin * 0.06)
        rx_max = max(rx_min + 2, smin * 0.13)

        max_attempts = target * 30
        for _ in range(max_attempts):
            if len(self.lily_pads) >= target:
                break
            rx = random.uniform(rx_min, rx_max)
            ry = rx * random.uniform(0.45, 0.65)  # flatter ellipses
            margin_x = rx + 2
            margin_y = ry + 2
            if (self.width - 2 * margin_x) < 1 or (self.phys_h - 2 * margin_y) < 1:
                continue
            cx = random.uniform(margin_x, self.width - margin_x)
            cy = random.uniform(margin_y, self.phys_h - margin_y)
            # Reject if too close to an existing pad
            ok = True
            for pad in self.lily_pads:
                dx = (cx - pad.cx) / max(rx, pad.rx)
                dy = (cy - pad.cy) / max(ry, pad.ry)
                if dx * dx + dy * dy < 1.6:  # ~1.25 radii apart
                    ok = False
                    break
            if not ok:
                continue
            self.lily_pads.append(
                LilyPad(cx, cy, rx, ry, random.uniform(0, 2 * math.pi)))

    def update(self):
        if self.paused:
            return
        for fish in self.fish_list:
            fish.update(self.speed_mult)

    def render(self, screen, ch):
        """Render the pond using a buffer + half-block output."""
        w, ph = self.width, self.phys_h
        # Build buffer:
        #   None                       -> water
        #   ('pad', shade)             -> lily pad cell
        #   (pattern, seg_idx, dist)   -> fish segment cell
        buffer = [[None] * w for _ in range(ph)]

        # Pads first so fish render on top of them
        for pad in self.lily_pads:
            self._stamp_lily_pad(buffer, pad, w, ph)

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

    def _stamp_lily_pad(self, buffer, pad, w, ph):
        """Rasterize an elliptical lily pad with V-notch and 3-tone shading."""
        rx, ry = pad.rx, pad.ry
        cx, cy = pad.cx, pad.cy
        # Iterate over the bounding box of the ellipse
        x0 = max(0, int(math.floor(cx - rx - 1)))
        x1 = min(w - 1, int(math.ceil(cx + rx + 1)))
        y0 = max(0, int(math.floor(cy - ry - 1)))
        y1 = min(ph - 1, int(math.ceil(cy + ry + 1)))

        nh = pad.notch_half_width
        notch_a = pad.notch_angle
        sox, soy = pad.shadow_offset
        # Shadow patch is a small darker region offset from center
        shadow_rx = rx * 0.45
        shadow_ry = ry * 0.45
        shadow_cx = cx + sox * rx * 0.4
        shadow_cy = cy + soy * ry * 0.4

        for py in range(y0, y1 + 1):
            dy = (py - cy) / ry
            for px in range(x0, x1 + 1):
                dx = (px - cx) / rx
                d_sq = dx * dx + dy * dy
                if d_sq > 1.0:
                    continue
                # Carve the V-notch: skip cells inside a small angular wedge
                ang = math.atan2(py - cy, px - cx)
                # Normalize angle difference to [-pi, pi]
                diff = (ang - notch_a + math.pi) % (2 * math.pi) - math.pi
                if abs(diff) < nh and d_sq > 0.05:
                    continue
                # Pick shade: rim near edge, shadow inside the small patch,
                # fill everywhere else
                if d_sq > 0.78:
                    shade = 'rim'
                else:
                    sdx = (px - shadow_cx) / max(0.1, shadow_rx)
                    sdy = (py - shadow_cy) / max(0.1, shadow_ry)
                    if sdx * sdx + sdy * sdy < 1.0:
                        shade = 'shadow'
                    else:
                        shade = 'fill'
                # Don't overwrite an existing pad cell with a lower-priority
                # shade (rim should not overwrite shadow, etc.)
                existing = buffer[py][px]
                if existing is not None and existing[0] == 'pad':
                    # Keep the more prominent shade: shadow > fill > rim
                    rank = {'shadow': 2, 'fill': 1, 'rim': 0}
                    if rank.get(shade, 0) <= rank.get(existing[1], 0):
                        continue
                buffer[py][px] = ('pad', shade)

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
                # Always overwrite water and pad cells. For fish-vs-fish,
                # keep the cell closer to a spine.
                if existing is None or existing[0] == 'pad' or dist < existing[2]:
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
                # Fins overwrite water and pads, but defer to other fish bodies
                if existing is None or existing[0] == 'pad':
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
        # Regenerate lily pads for the new pond dimensions
        self._init_lily_pads()

    def add_fish(self):
        from .themes import KOI_PATTERN_NAMES
        x = random.uniform(15, max(16, self.width - 15))
        y = random.uniform(15, max(16, self.phys_h - 15))
        pattern = random.choice(KOI_PATTERN_NAMES)
        self.fish_list.append(Fish(x, y, self.width, self.phys_h, pattern))

    def remove_fish(self):
        if len(self.fish_list) > 1:
            self.fish_list.pop()
