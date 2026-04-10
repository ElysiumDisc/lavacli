"""Main application loop for LavaCLI."""
import curses
import locale
import time

from .lamp import Lamp, SIZE_DEFAULTS
from .menu import show_menu
from .pond import Pond
from .themes import ColorHelper, THEME_ORDER


def calculate_lamp_dims(term_w, term_h, count, size_pref, style='classic'):
    """Calculate lamp body dimensions to fit the terminal."""
    defaults = SIZE_DEFAULTS[size_pref]

    # Freestyle: fill the entire terminal
    if style == 'freestyle':
        body_w = term_w
        body_h = term_h - 1  # leave 1 row for HUD
        num_balls = max(8, defaults['num_balls'] * 2)
        # Scale radius for larger area
        area_scale = (body_w * body_h) / (defaults['body_width'] * defaults['body_height'])
        ball_r = defaults['ball_radius'] * max(1.0, min(2.0, area_scale ** 0.3))
        return body_w, body_h, num_balls, ball_r, 0, 0

    usable_w = term_w - 2
    usable_h = term_h - 3  # HUD + margin

    # Width: fit all lamps with gaps
    gap = max(1, min(4, usable_w // (count + 1) // 4))
    lamp_slot_w = (usable_w - gap * (count + 1)) // max(1, count)
    body_w = max(6, min(defaults['body_width'], lamp_slot_w - 2))

    # Height: scale ALL parts proportionally to fit terminal
    # Keep real lamp proportions: body ~55%, base ~35%, cap ~10%
    total_default = (defaults['body_height'] + defaults['base_height']
                     + defaults['cap_height'])
    max_total = usable_h - 1
    scale = min(1.0, max_total / total_default) if total_default > 0 else 1.0

    body_h = max(6, int(defaults['body_height'] * scale))
    base_h = max(4, int(defaults['base_height'] * scale))
    cap_h = max(2, int(defaults['cap_height'] * scale))

    # Rocket style: taller pointed nose cone and fin base
    if style == 'rocket':
        cap_h = max(5, int(cap_h * 2.2))
        base_h = max(5, int(base_h * 1.2))

    # Scale ball radius
    w_scale = body_w / defaults['body_width'] if defaults['body_width'] > 0 else 1.0
    ball_r = defaults['ball_radius'] * max(0.5, min(1.5, w_scale))

    return body_w, body_h, defaults['num_balls'], ball_r, base_h, cap_h


def layout_lamps(lamps, term_w, term_h):
    """Calculate screen positions for all lamps."""
    total_w = sum(lamp.total_width for lamp in lamps)
    gap = max(1, (term_w - total_w) // (len(lamps) + 1))

    positions = []
    x = gap
    for lamp in lamps:
        y = max(0, (term_h - lamp.total_height - 2) // 2)
        positions.append((x, y))
        x += lamp.total_width + gap

    return positions


def draw_shelf(screen, positions, lamps, term_w, ch):
    """Draw a decorative shelf under all lamps."""
    if not positions:
        return
    max_bottom = 0
    for (x, y), lamp in zip(positions, lamps):
        max_bottom = max(max_bottom, y + lamp.total_height)

    shelf_y = max_bottom
    attr = ch.base_attr | curses.A_DIM
    try:
        for c in range(1, term_w - 1):
            screen.addstr(shelf_y, c, '\u2550', attr)
    except curses.error:
        pass


def draw_hud(screen, term_h, term_w, lamps, ch, speed):
    """Draw the controls bar at the bottom."""
    hud_y = term_h - 1
    paused = lamps[0].paused if lamps else False
    parts = [
        'Q:Quit',
        'M:Menu',
        '+/-:Speed({:.0f}%)'.format(speed * 100),
        'Space:Resume' if paused else 'Space:Pause',
        'C:Colors',
        'B/V:Blobs',
        'R:Reset',
        'H:Hide',
    ]
    hud = '  '.join(parts)
    try:
        screen.addstr(hud_y, max(0, (term_w - len(hud)) // 2),
                      hud, ch.text_attr | curses.A_DIM)
    except curses.error:
        pass


def run():
    """Entry point for the lava lamp application."""
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(_main)


def _main(screen):
    curses.curs_set(0)
    screen.keypad(True)

    while True:
        config = show_menu(screen)
        if config is None:
            return

        if config['style'] == 'koipond':
            result = _run_pond(screen, config)
        else:
            result = _run_lamp(screen, config)

        if result:
            continue  # M pressed: back to menu
        else:
            break     # Q pressed: quit


def _run_lamp(screen, config):
    """Run the lamp animation. Returns True to go back to menu, False to quit."""
    ch = ColorHelper(config['theme'])
    ch.setup()

    is_freestyle = config['style'] == 'freestyle'
    lamp_count = 1 if is_freestyle else config['count']

    term_h, term_w = screen.getmaxyx()
    body_w, body_h, num_balls, ball_r, base_h, cap_h = calculate_lamp_dims(
        term_w, term_h, lamp_count, config['size'], config['style'])

    lamps = []
    for _ in range(lamp_count):
        lamps.append(Lamp(config['style'], body_w, body_h,
                          config['flow'], num_balls, ball_r, base_h, cap_h,
                          freestyle=is_freestyle))

    positions = layout_lamps(lamps, term_w, term_h) if not is_freestyle else [(0, 0)]
    theme_idx = THEME_ORDER.index(config['theme'])
    show_hud = True

    frame_ms = 50  # ~20 fps
    screen.timeout(frame_ms)

    while True:
        frame_start = time.monotonic()

        key = screen.getch()

        if key in (ord('q'), ord('Q'), 27):
            return False
        elif key in (ord('m'), ord('M')):
            return True
        elif key == curses.KEY_RESIZE:
            term_h, term_w = screen.getmaxyx()
            body_w, body_h, _, ball_r, base_h, cap_h = calculate_lamp_dims(
                term_w, term_h, len(lamps), config['size'], config['style'])
            for lamp in lamps:
                lamp.resize(body_w, body_h, base_h, cap_h)
            positions = layout_lamps(lamps, term_w, term_h) if not is_freestyle else [(0, 0)]
        elif key == ord(' '):
            for lamp in lamps:
                lamp.paused = not lamp.paused
        elif key in (ord('+'), ord('=')):
            for lamp in lamps:
                lamp.speed_mult = min(3.0, lamp.speed_mult + 0.25)
        elif key in (ord('-'), ord('_')):
            for lamp in lamps:
                lamp.speed_mult = max(0.25, lamp.speed_mult - 0.25)
        elif key in (ord('c'), ord('C')):
            theme_idx = (theme_idx + 1) % len(THEME_ORDER)
            ch.change_theme(THEME_ORDER[theme_idx])
        elif key in (ord('b'), ord('B')):
            for lamp in lamps:
                lamp.add_ball()
        elif key in (ord('v'), ord('V')):
            for lamp in lamps:
                lamp.remove_ball()
        elif key in (ord('h'), ord('H')):
            show_hud = not show_hud
        elif key in (ord('r'), ord('R')):
            lamps.clear()
            body_w, body_h, num_balls, ball_r, base_h, cap_h = calculate_lamp_dims(
                term_w, term_h, lamp_count, config['size'], config['style'])
            for _ in range(lamp_count):
                lamps.append(Lamp(config['style'], body_w, body_h,
                                  config['flow'], num_balls, ball_r, base_h, cap_h,
                                  freestyle=is_freestyle))
            positions = layout_lamps(lamps, term_w, term_h) if not is_freestyle else [(0, 0)]

        for lamp in lamps:
            lamp.update()

        screen.erase()

        for lamp, (x, y) in zip(lamps, positions):
            if is_freestyle:
                lamp.render_freestyle(screen, x, y, ch)
            else:
                lamp.render(screen, x, y, ch)

        if not is_freestyle:
            draw_shelf(screen, positions, lamps, term_w, ch)
        if show_hud:
            draw_hud(screen, term_h, term_w, lamps, ch,
                     lamps[0].speed_mult if lamps else 1.0)

        try:
            screen.noutrefresh()
            curses.doupdate()
        except curses.error:
            pass

        elapsed = time.monotonic() - frame_start
        remaining = (frame_ms / 1000.0) - elapsed
        if remaining > 0:
            time.sleep(remaining * 0.5)


def draw_pond_hud(screen, term_h, term_w, pond, ch):
    """Draw the controls bar for koi pond mode."""
    hud_y = term_h - 1
    parts = [
        'Q:Quit',
        'M:Menu',
        '+/-:Speed({:.0f}%)'.format(pond.speed_mult * 100),
        'Space:Resume' if pond.paused else 'Space:Pause',
        'C:Colors',
        'B/V:Fish',
        'R:Reset',
        'H:Hide',
    ]
    hud = '  '.join(parts)
    try:
        screen.addstr(hud_y, max(0, (term_w - len(hud)) // 2),
                      hud, ch.text_attr | curses.A_DIM)
    except curses.error:
        pass


def _run_pond(screen, config):
    """Run the koi pond animation. Returns True to go back to menu, False to quit."""
    ch = ColorHelper(config['theme'])
    ch.setup()
    ch.setup_pond_colors()

    term_h, term_w = screen.getmaxyx()
    # Map count (1-6) to fish count (3-12)
    fish_count = max(3, config.get('count', 1) * 2 + 1)

    pond = Pond(term_w, term_h - 1, fish_count)
    theme_idx = THEME_ORDER.index(config['theme'])
    show_hud = True

    frame_ms = 50  # ~20 fps
    screen.timeout(frame_ms)

    while True:
        frame_start = time.monotonic()

        key = screen.getch()

        if key in (ord('q'), ord('Q'), 27):
            return False
        elif key in (ord('m'), ord('M')):
            return True
        elif key == curses.KEY_RESIZE:
            term_h, term_w = screen.getmaxyx()
            pond.resize(term_w, term_h - 1)
        elif key == ord(' '):
            pond.paused = not pond.paused
        elif key in (ord('+'), ord('=')):
            pond.speed_mult = min(3.0, pond.speed_mult + 0.25)
        elif key in (ord('-'), ord('_')):
            pond.speed_mult = max(0.25, pond.speed_mult - 0.25)
        elif key in (ord('c'), ord('C')):
            theme_idx = (theme_idx + 1) % len(THEME_ORDER)
            ch.change_theme(THEME_ORDER[theme_idx])
            ch.setup_pond_colors()
        elif key in (ord('b'), ord('B')):
            pond.add_fish()
        elif key in (ord('v'), ord('V')):
            pond.remove_fish()
        elif key in (ord('h'), ord('H')):
            show_hud = not show_hud
        elif key in (ord('r'), ord('R')):
            pond = Pond(term_w, term_h - 1, fish_count, pond.speed_mult)

        pond.update()

        screen.erase()
        pond.render(screen, ch)

        if show_hud:
            draw_pond_hud(screen, term_h, term_w, pond, ch)

        try:
            screen.noutrefresh()
            curses.doupdate()
        except curses.error:
            pass

        elapsed = time.monotonic() - frame_start
        remaining = (frame_ms / 1000.0) - elapsed
        if remaining > 0:
            time.sleep(remaining * 0.5)
