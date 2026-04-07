"""Interactive selection menu for LavaCLI with groovy animated lava background."""
import curses
import math
import random
import time

from .lamp import SHAPE_ORDER, FLOW_ORDER, SIZE_ORDER, SIZE_NAMES, Ball
from .themes import THEMES, THEME_ORDER, ColorHelper

TITLE = [
    '  .  *  .    L A V A C L I    .  *  .',
    ' ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',
]

TAGLINES = [
    'Far out!',
    'Groovy vibes, man.',
    'Peace, love & lava.',
    'Keep on flowin\'.',
    'Feelin\' the flow.',
    'Totally tubular.',
    'Mellow yellow.',
    'Ride the wave.',
    'Stay groovy.',
    'Liquid dreams.',
]

FIELDS = [
    ('STYLE', [s.capitalize() for s in SHAPE_ORDER]),
    ('THEME', [THEMES[t]['name'] for t in THEME_ORDER]),
    ('FLOW', [f.capitalize() for f in FLOW_ORDER]),
    ('COUNT', [str(i) for i in range(1, 7)]),
    ('SIZE', [SIZE_NAMES[s] for s in SIZE_ORDER]),
]

# Default selections: classic, retro_red, classic, 1 lamp, Grande (27")
DEFAULT_SELECTIONS = [0, 0, 0, 0, 4]


class _MenuLava:
    """Lightweight lava simulation for the menu background."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.phys_h = height * 2
        self.balls = []
        num = max(3, min(5, width // 20))
        for _ in range(num):
            x = random.uniform(1, width - 1)
            y = random.uniform(1, self.phys_h - 1)
            b = Ball(x, y, max(3.0, width * 0.15))
            b.vx = random.uniform(-0.3, 0.3)
            b.vy = random.uniform(-0.3, 0.3)
            b.temp = random.uniform(0.3, 0.7)
            self.balls.append(b)

    def update(self):
        for ball in self.balls:
            # Gentle floating motion
            ball.vx += random.gauss(0, 0.02)
            ball.vy += random.gauss(0, 0.02)
            ball.vx *= 0.96
            ball.vy *= 0.96
            ball.x += ball.vx
            ball.y += ball.vy

            # Bounce off edges
            if ball.x < 1:
                ball.x = 1
                ball.vx = abs(ball.vx)
            elif ball.x > self.width - 1:
                ball.x = self.width - 1
                ball.vx = -abs(ball.vx)
            if ball.y < 1:
                ball.y = 1
                ball.vy = abs(ball.vy)
            elif ball.y > self.phys_h - 1:
                ball.y = self.phys_h - 1
                ball.vy = -abs(ball.vy)

    def field_at(self, px, py):
        total = 0.0
        for ball in self.balls:
            dx = px - ball.x
            dy = (py - ball.y) * 0.55
            d_sq = dx * dx + dy * dy
            if d_sq < 0.001:
                d_sq = 0.001
            total += (ball.radius * ball.radius) / d_sq
        return total

    def resize(self, width, height):
        old_w, old_h = self.width, self.phys_h
        self.width = width
        self.height = height
        self.phys_h = height * 2
        for ball in self.balls:
            ball.x = ball.x * width / old_w if old_w > 0 else width / 2
            ball.y = ball.y * self.phys_h / old_h if old_h > 0 else self.phys_h / 2


def _field_to_bg_level(field):
    """Simpler threshold for dim background lava."""
    if field < 0.4:
        return 0
    elif field < 0.8:
        return 6  # rim
    elif field < 1.5:
        return 1
    elif field < 2.5:
        return 2
    else:
        return 3


def _render_bg(screen, lava, ch, height, width):
    """Render dim lava background behind menu."""
    # Sample every other column for performance
    for row in range(height):
        py_t = row * 2
        py_b = row * 2 + 1
        for col in range(width):
            ft = lava.field_at(col + 0.5, py_t + 0.5)
            fb = lava.field_at(col + 0.5, py_b + 0.5)
            tl = _field_to_bg_level(ft)
            bl = _field_to_bg_level(fb)
            if tl == 0 and bl == 0:
                continue
            ch.draw_cell(screen, row, col, tl, bl)


def show_menu(screen):
    """Display the interactive configuration menu. Returns config dict or None."""
    curses.curs_set(0)
    screen.clear()

    selections = list(DEFAULT_SELECTIONS)
    current_field = 0

    height, width = screen.getmaxyx()

    # Set up color helper for menu background
    ch = ColorHelper(THEME_ORDER[selections[1]])
    ch.setup()

    # Create background lava
    lava = _MenuLava(width, height)

    tagline_idx = random.randint(0, len(TAGLINES) - 1)
    frame_count = 0
    screen.timeout(70)

    while True:
        screen.erase()
        height, width = screen.getmaxyx()

        if height < 20 or width < 46:
            try:
                screen.addstr(0, 0, 'Terminal too small. Resize to at least 46x20.')
            except curses.error:
                pass
            screen.refresh()
            screen.getch()
            continue

        # Update and render background lava
        lava.update()
        _render_bg(screen, lava, ch, height, width)

        # Rotate tagline every ~3 seconds (~43 frames at 70ms)
        frame_count += 1
        if frame_count % 43 == 0:
            tagline_idx = (tagline_idx + 1) % len(TAGLINES)

        menu_width = 48
        menu_height = len(TITLE) + len(FIELDS) * 2 + 12
        sx = max(0, (width - menu_width) // 2)
        sy = max(0, (height - menu_height) // 2)

        # Decorative top border
        border_top = '\u2554' + '\u2550' * (menu_width - 2) + '\u2557'
        border_bot = '\u255a' + '\u2550' * (menu_width - 2) + '\u255d'
        border_side_l = '\u2551'
        border_side_r = '\u2551'
        try:
            screen.addstr(sy, sx, border_top, ch.accent_attr)
            screen.addstr(sy + menu_height - 1, sx, border_bot, ch.accent_attr)
            for r in range(1, menu_height - 1):
                screen.addstr(sy + r, sx, border_side_l, ch.accent_attr)
                screen.addstr(sy + r, sx + menu_width - 1, border_side_r,
                              ch.accent_attr)
        except curses.error:
            pass

        # Title with accent color (centered within the box)
        title_y = sy + 2
        for i, line in enumerate(TITLE):
            try:
                x = sx + max(0, (menu_width - len(line)) // 2)
                screen.addstr(title_y + i, x, line,
                              ch.accent_attr | curses.A_BOLD)
            except curses.error:
                pass

        # Tagline (centered within the box)
        tagline = TAGLINES[tagline_idx]
        try:
            tx = sx + max(0, (menu_width - len(tagline)) // 2)
            screen.addstr(title_y + len(TITLE) + 1, tx,
                          tagline, ch.text_attr | curses.A_DIM)
        except curses.error:
            pass

        # Separator (fits inside the box)
        sep_y = title_y + len(TITLE) + 3
        sep = '\u2500' * (menu_width - 4)
        try:
            screen.addstr(sep_y, sx + 2, sep, ch.accent_attr | curses.A_DIM)
        except curses.error:
            pass

        # Fields -- show only the selected option, contained within the box
        field_y = sep_y + 2
        label_col = sx + 2
        value_col = sx + 12
        max_val_w = menu_width - 14  # space available for value text

        for fi, (label, options) in enumerate(FIELDS):
            y = field_y + fi * 2
            is_active = fi == current_field
            sel = selections[fi]
            opt = options[sel]

            # Label
            prefix = '\u25b8 ' if is_active else '  '
            label_attr = ch.accent_attr | curses.A_BOLD if is_active else curses.A_DIM
            try:
                screen.addstr(y, label_col, prefix + label, label_attr)
            except curses.error:
                pass

            # Selected value with arrows
            arrow_l = '\u25c2 '
            arrow_r = ' \u25b8'
            val_text = arrow_l + opt + arrow_r
            # Truncate if too wide
            if len(val_text) > max_val_w:
                val_text = val_text[:max_val_w - 1] + '\u2026'

            if is_active:
                val_attr = ch.accent_attr | curses.A_BOLD | curses.A_REVERSE
            else:
                val_attr = curses.A_BOLD
            try:
                screen.addstr(y, value_col, val_text, val_attr)
            except curses.error:
                pass

        # Launch button (centered within the box)
        btn_y = field_y + len(FIELDS) * 2 + 1
        btn_text = '\u2605 ENTER TO LAUNCH \u2605'
        is_btn = current_field == len(FIELDS)
        btn_attr = (ch.accent_attr | curses.A_BOLD | curses.A_REVERSE
                    if is_btn else ch.accent_attr | curses.A_BOLD)
        try:
            bx = sx + max(0, (menu_width - len(btn_text)) // 2)
            screen.addstr(btn_y, bx, btn_text, btn_attr)
        except curses.error:
            pass

        # Help (centered within the box)
        help_y = btn_y + 3
        help_text = '\u2191\u2193 Navigate  \u2190\u2192 Change  Enter  Q Quit'
        try:
            hx = sx + max(0, (menu_width - len(help_text)) // 2)
            screen.addstr(help_y, hx, help_text, curses.A_DIM)
        except curses.error:
            pass

        screen.refresh()

        key = screen.getch()

        if key == -1:
            continue
        elif key == ord('q') or key == ord('Q') or key == 27:
            return None
        elif key == curses.KEY_UP or key == ord('k'):
            current_field = max(0, current_field - 1)
        elif key == curses.KEY_DOWN or key == ord('j'):
            current_field = min(len(FIELDS), current_field + 1)
        elif key == curses.KEY_LEFT or key == ord('h'):
            if current_field < len(FIELDS):
                n = len(FIELDS[current_field][1])
                selections[current_field] = (selections[current_field] - 1) % n
                # Live theme preview: re-init colors when theme changes
                if current_field == 1:
                    ch.change_theme(THEME_ORDER[selections[1]])
        elif key == curses.KEY_RIGHT or key == ord('l'):
            if current_field < len(FIELDS):
                n = len(FIELDS[current_field][1])
                selections[current_field] = (selections[current_field] + 1) % n
                if current_field == 1:
                    ch.change_theme(THEME_ORDER[selections[1]])
        elif key in (ord('\n'), curses.KEY_ENTER, 10):
            return {
                'style': SHAPE_ORDER[selections[0]],
                'theme': THEME_ORDER[selections[1]],
                'flow': FLOW_ORDER[selections[2]],
                'count': selections[3] + 1,
                'size': SIZE_ORDER[selections[4]],
            }
        elif key == curses.KEY_RESIZE:
            height, width = screen.getmaxyx()
            lava.resize(width, height)
