"""Main application loop for LavaCLI."""
import curses
import locale
import time

from .lamp import Lamp, SIZE_DEFAULTS
from .menu import show_menu
from .themes import ColorHelper, THEME_ORDER


def calculate_lamp_dims(term_w, term_h, count, size_pref):
    """Calculate lamp body dimensions to fit the terminal."""
    defaults = SIZE_DEFAULTS[size_pref]
    usable_w = term_w - 2
    usable_h = term_h - 6  # room for HUD + margins

    # Width: fit all lamps with gaps
    gap = max(1, min(4, usable_w // (count + 1) // 4))
    lamp_slot_w = (usable_w - gap * (count + 1)) // count
    body_w = max(6, min(defaults['body_width'], lamp_slot_w - 4))

    # Height: fit within terminal
    max_body_h = usable_h - Lamp.CAP_HEIGHT - Lamp.BASE_HEIGHT
    body_h = max(6, min(defaults['body_height'], max_body_h))

    # Scale ball radius with size
    scale = min(body_w / defaults['body_width'], body_h / defaults['body_height'])
    ball_r = defaults['ball_radius'] * max(0.5, min(1.5, scale))

    return body_w, body_h, defaults['num_balls'], ball_r


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

    # Find the lowest point of all lamps
    max_bottom = 0
    for (x, y), lamp in zip(positions, lamps):
        bottom = y + lamp.total_height
        max_bottom = max(max_bottom, bottom)

    shelf_y = max_bottom
    attr = ch.base_attr

    try:
        for c in range(1, term_w - 1):
            screen.addstr(shelf_y, c, '\u2550', attr)
    except curses.error:
        pass


def draw_hud(screen, term_h, term_w, lamps, ch, speed):
    """Draw the controls bar at the bottom."""
    hud_y = term_h - 1

    parts = [
        'Q:Quit',
        '+/-:Speed({:.0f}%)'.format(speed * 100),
        'Space:Pause' if not lamps[0].paused else 'Space:Resume',
        'C:Colors',
        'B/V:Blobs',
        'R:Reset',
    ]
    hud = '  '.join(parts)

    try:
        screen.addstr(hud_y, max(0, (term_w - len(hud)) // 2), hud, ch.text_attr | curses.A_DIM)
    except curses.error:
        pass


def run():
    """Entry point for the lava lamp application."""
    locale.setlocale(locale.LC_ALL, '')
    curses.wrapper(_main)


def _main(screen):
    """Main curses application."""
    # Setup
    curses.curs_set(0)
    screen.keypad(True)

    # Show menu
    config = show_menu(screen)
    if config is None:
        return

    # Create color helper
    ch = ColorHelper(config['theme'])
    ch.setup()

    # Create lamps
    term_h, term_w = screen.getmaxyx()
    body_w, body_h, num_balls, ball_r = calculate_lamp_dims(
        term_w, term_h, config['count'], config['size'])

    lamps = []
    for _ in range(config['count']):
        lamp = Lamp(config['style'], body_w, body_h,
                    config['flow'], num_balls, ball_r)
        lamps.append(lamp)

    positions = layout_lamps(lamps, term_w, term_h)

    # Theme cycling index
    theme_idx = THEME_ORDER.index(config['theme'])

    # Animation loop
    frame_ms = 75  # ~13 fps
    screen.timeout(frame_ms)

    while True:
        frame_start = time.monotonic()

        # Handle input
        key = screen.getch()

        if key == ord('q') or key == ord('Q') or key == 27:
            break

        elif key == curses.KEY_RESIZE:
            term_h, term_w = screen.getmaxyx()
            body_w, body_h, _, ball_r = calculate_lamp_dims(
                term_w, term_h, len(lamps), config['size'])
            for lamp in lamps:
                lamp.resize(body_w, body_h)
            positions = layout_lamps(lamps, term_w, term_h)

        elif key == ord(' '):
            for lamp in lamps:
                lamp.paused = not lamp.paused

        elif key == ord('+') or key == ord('='):
            for lamp in lamps:
                lamp.speed_mult = min(3.0, lamp.speed_mult + 0.25)

        elif key == ord('-') or key == ord('_'):
            for lamp in lamps:
                lamp.speed_mult = max(0.25, lamp.speed_mult - 0.25)

        elif key == ord('c') or key == ord('C'):
            theme_idx = (theme_idx + 1) % len(THEME_ORDER)
            ch.change_theme(THEME_ORDER[theme_idx])

        elif key == ord('b') or key == ord('B'):
            for lamp in lamps:
                lamp.add_ball()

        elif key == ord('v') or key == ord('V'):
            for lamp in lamps:
                lamp.remove_ball()

        elif key == ord('r') or key == ord('R'):
            # Reset lamps
            lamps.clear()
            body_w, body_h, num_balls, ball_r = calculate_lamp_dims(
                term_w, term_h, config['count'], config['size'])
            for _ in range(config['count']):
                lamps.append(Lamp(config['style'], body_w, body_h,
                                  config['flow'], num_balls, ball_r))
            positions = layout_lamps(lamps, term_w, term_h)

        # Update physics
        for lamp in lamps:
            lamp.update()

        # Render
        screen.erase()

        for lamp, (x, y) in zip(lamps, positions):
            lamp.render(screen, x, y, ch)

        draw_shelf(screen, positions, lamps, term_w, ch)
        draw_hud(screen, term_h, term_w, lamps, ch, lamps[0].speed_mult if lamps else 1.0)

        try:
            screen.noutrefresh()
            curses.doupdate()
        except curses.error:
            pass

        # Frame timing - account for processing time
        elapsed = time.monotonic() - frame_start
        remaining = (frame_ms / 1000.0) - elapsed
        if remaining > 0:
            time.sleep(remaining * 0.5)  # partial sleep, getch timeout handles the rest
