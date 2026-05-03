"""Main application loop for LavaCLI."""
import argparse
import curses
import locale
import random
import time

from . import __version__
from .donut import Donut
from .lamp import Lamp, SHAPE_ORDER, FLOW_ORDER, SIZE_ORDER, SIZE_DEFAULTS
from .menu import show_menu
from .pond import Pond
from .themes import ColorHelper, THEME_ORDER


def _positive_int_range(lo, hi):
    def parse(value):
        try:
            n = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                '{!r} is not an integer'.format(value))
        if not (lo <= n <= hi):
            raise argparse.ArgumentTypeError(
                '{} out of range [{}, {}]'.format(n, lo, hi))
        return n
    return parse


def _build_parser():
    p = argparse.ArgumentParser(
        prog='lavacli',
        description='A beautiful, interactive terminal lava lamp simulator.')
    p.add_argument('--version', action='version',
                   version='lavacli {}'.format(__version__))
    p.add_argument('--style', choices=SHAPE_ORDER,
                   help='Lamp style (skips menu)')
    p.add_argument('--theme', choices=THEME_ORDER,
                   help='Color theme (skips menu)')
    p.add_argument('--flow', choices=FLOW_ORDER,
                   help='Flow type (skips menu)')
    p.add_argument('--count', type=_positive_int_range(1, 6),
                   help='Number of lamps, 1-6 (skips menu)')
    p.add_argument('--size', choices=SIZE_ORDER,
                   help='Lamp size preset (skips menu)')
    p.add_argument('--random', action='store_true',
                   help='Randomize all unspecified fields (skips menu)')
    p.add_argument('--duration', type=_positive_int_range(1, 86400),
                   metavar='SECONDS',
                   help='Run for N seconds then exit (for screensaver use)')
    p.add_argument('--bicolor', choices=THEME_ORDER,
                   metavar='THEME_B',
                   help='Mix a second theme into the lava (90s bi-color lamp)')
    return p


def _config_from_args(args):
    """Build a menu-style config dict from CLI args.

    Returns None if no direct-launch flags were set (menu should run).
    """
    direct_flags = (args.style, args.theme, args.flow,
                    args.count, args.size)
    if not any(f is not None for f in direct_flags) and not args.random:
        return None

    if args.random:
        style = random.choice(SHAPE_ORDER)
        theme = random.choice(THEME_ORDER)
        flow = random.choice(FLOW_ORDER)
        count = random.randint(1, 6)
        size = random.choice(SIZE_ORDER)
    else:
        style = 'classic'
        theme = THEME_ORDER[0]
        flow = 'classic'
        count = 1
        size = 'G'

    if args.style is not None:
        style = args.style
    if args.theme is not None:
        theme = args.theme
    if style == 'campfire' and theme != 'campfire':
        theme = 'campfire'
    if style == 'xmas' and theme != 'xmas':
        theme = 'xmas'
    if args.flow is not None:
        flow = args.flow
    if args.count is not None:
        count = args.count
    if args.size is not None:
        size = args.size

    return {
        'style': style,
        'theme': theme,
        'flow': flow,
        'count': count,
        'size': size,
        'bicolor': args.bicolor,
    }


def calculate_lamp_dims(term_w, term_h, count, size_pref, style='classic'):
    """Calculate lamp body dimensions to fit the terminal."""
    defaults = SIZE_DEFAULTS[size_pref]

    # Fullscreen styles (freestyle / fireplace): fill the whole terminal.
    # Fireplace uses smaller, more numerous embers, handled in Lamp.__init__.
    if style in ('freestyle', 'fireplace', 'campfire', 'xmas'):
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


def draw_hud(screen, term_h, term_w, lamps, ch, speed,
              trails=False, bicolor=False, style=None):
    """Draw the controls bar at the bottom."""
    hud_y = term_h - 1
    paused = lamps[0].paused if lamps else False
    _FLAME_NAMES = ('Small', 'Medium', 'Large')
    bv_label = ('B/V:Flame({})'.format(_FLAME_NAMES[lamps[0].flame_size])
                if style == 'xmas' and lamps else 'B/V:Blobs')
    parts = [
        'Q:Quit',
        'M:Menu',
        '+/-:Speed({:.0f}%)'.format(speed * 100),
        'Space:Resume' if paused else 'Space:Pause',
        'C:Colors',
        bv_label,
        'T:Trails*' if trails else 'T:Trails',
        'R:Reset',
        'H:Hide',
    ]
    if bicolor:
        parts.append('[A+B]')
    hud = '  '.join(parts)
    try:
        screen.addstr(hud_y, max(0, (term_w - len(hud)) // 2),
                      hud, ch.text_attr | curses.A_DIM)
    except curses.error:
        pass


def draw_donut_hud(screen, term_h, term_w, donut, ch):
    """Draw the controls bar for donut mode."""
    from .donut import SHADE_MODE_NAMES
    hud_y = term_h - 1
    parts = [
        'Q:Quit',
        'M:Menu',
        '+/-:Speed({:.0f}%)'.format(donut.speed_mult * 100),
        'Space:Resume' if donut.paused else 'Space:Pause',
        'C:Theme',
        'B/V:Shade({})'.format(SHADE_MODE_NAMES[donut.shade_mode]),
        'R:Reset',
        'H:Hide',
    ]
    hud = '  '.join(parts)
    try:
        screen.addstr(hud_y, max(0, (term_w - len(hud)) // 2),
                      hud, ch.text_attr | curses.A_DIM)
    except curses.error:
        pass


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


def _run_animation(screen, deadline, ch, state, draw_fn, update_fn,
                   draw_hud_fn, handle_key_fn, reset_fn, frame_ms=50):
    """Generic animation loop shared by lamp, donut, and pond modes.

    Returns True to go back to menu, False to quit.

    Callbacks (all receive/return state dict for mutable shared state):
        draw_fn(screen, state, ch)          — render one frame
        update_fn(state)                    — advance physics/state
        draw_hud_fn(screen, state, ch)      — draw HUD bar
        handle_key_fn(key, state, ch)       — return True if loop should exit
        reset_fn(state, ch)                 — recreate animation object(s)
    """
    screen.timeout(frame_ms)
    show_hud = state.setdefault('show_hud', True)

    while True:
        if deadline is not None and time.monotonic() >= deadline:
            return False

        frame_start = time.monotonic()
        key = screen.getch()

        if key in (ord('q'), ord('Q'), 27):
            return False
        elif key in (ord('m'), ord('M')):
            return True
        elif key in (ord('h'), ord('H')):
            show_hud = not show_hud
        elif key != -1:
            if handle_key_fn(key, state, ch):
                return state.pop('_exit_result', False)

        update_fn(state)

        screen.erase()
        draw_fn(screen, state, ch)

        if show_hud:
            draw_hud_fn(screen, state, ch)

        try:
            screen.noutrefresh()
            curses.doupdate()
        except curses.error:
            pass

        elapsed = time.monotonic() - frame_start
        remaining = (frame_ms / 1000.0) - elapsed
        if remaining > 0:
            time.sleep(remaining)


def run(argv=None):
    """Entry point for the lava lamp application."""
    locale.setlocale(locale.LC_ALL, '')
    args = _build_parser().parse_args(argv)
    curses.wrapper(_main, args)


def _main(screen, args):
    curses.curs_set(0)
    screen.keypad(True)

    direct_config = _config_from_args(args)
    deadline = None
    if args.duration is not None:
        deadline = time.monotonic() + args.duration

    # Direct-launch mode: skip menu entirely, run once, exit.
    if direct_config is not None:
        if direct_config['style'] == 'koipond':
            _run_pond(screen, direct_config, deadline=deadline)
        elif direct_config['style'] == 'donut':
            _run_donut(screen, direct_config, deadline=deadline)
        else:
            _run_lamp(screen, direct_config, deadline=deadline)
        return

    while True:
        config = show_menu(screen)
        if config is None:
            return

        if config['style'] == 'koipond':
            result = _run_pond(screen, config, deadline=deadline)
        elif config['style'] == 'donut':
            result = _run_donut(screen, config, deadline=deadline)
        else:
            result = _run_lamp(screen, config, deadline=deadline)

        if result:
            continue  # M pressed: back to menu
        else:
            break     # Q pressed: quit


def _run_lamp(screen, config, deadline=None):
    """Run the lamp animation. Returns True to go back to menu, False to quit."""
    ch = ColorHelper(config['theme'])
    ch.setup()
    bicolor_theme = config.get('bicolor')
    if bicolor_theme:
        ch.set_secondary_theme(bicolor_theme)

    is_fullscreen = config['style'] in ('freestyle', 'fireplace', 'campfire', 'xmas')
    lamp_count = 1 if is_fullscreen else config['count']

    term_h, term_w = screen.getmaxyx()
    body_w, body_h, num_balls, ball_r, base_h, cap_h = calculate_lamp_dims(
        term_w, term_h, lamp_count, config['size'], config['style'])

    lamps = []
    for _ in range(lamp_count):
        lamps.append(Lamp(config['style'], body_w, body_h,
                          config['flow'], num_balls, ball_r, base_h, cap_h,
                          freestyle=is_fullscreen,
                          bicolor=bool(bicolor_theme)))

    positions = layout_lamps(lamps, term_w, term_h) if not is_fullscreen else [(0, 0)]

    state = {
        'ch': ch, 'lamps': lamps, 'positions': positions,
        'term_h': term_h, 'term_w': term_w,
        'theme_idx': THEME_ORDER.index(config['theme']),
        'is_fullscreen': is_fullscreen, 'lamp_count': lamp_count,
        'bicolor_theme': bicolor_theme,
    }

    def _update(st):
        for lamp in st['lamps']:
            lamp.update()

    def _draw(scr, st, ch_):
        for lamp, (x, y) in zip(st['lamps'], st['positions']):
            if st['is_fullscreen']:
                lamp.render_freestyle(scr, x, y, ch_)
            else:
                lamp.render(scr, x, y, ch_)
        if not st['is_fullscreen']:
            draw_shelf(scr, st['positions'], st['lamps'], st['term_w'], ch_)

    def _draw_hud_fn(scr, st, ch_):
        draw_hud(scr, st['term_h'], st['term_w'], st['lamps'], ch_,
                 st['lamps'][0].speed_mult if st['lamps'] else 1.0,
                 trails=bool(st['lamps'] and st['lamps'][0].trails),
                 bicolor=bool(st['bicolor_theme']),
                 style=config['style'])

    def _handle_key(key, st, ch_):
        if key == curses.KEY_RESIZE:
            th, tw = scr.getmaxyx()
            st['term_h'], st['term_w'] = th, tw
            bw, bh, _, br, bhh, chh = calculate_lamp_dims(
                tw, th, len(st['lamps']), config['size'], config['style'])
            for lamp in st['lamps']:
                lamp.resize(bw, bh, bhh, chh, br)
            st['positions'] = (layout_lamps(st['lamps'], tw, th)
                               if not st['is_fullscreen'] else [(0, 0)])
        elif key == ord(' '):
            for lamp in st['lamps']:
                lamp.paused = not lamp.paused
        elif key in (ord('+'), ord('=')):
            for lamp in st['lamps']:
                lamp.speed_mult = min(3.0, lamp.speed_mult + 0.25)
        elif key in (ord('-'), ord('_')):
            for lamp in st['lamps']:
                lamp.speed_mult = max(0.25, lamp.speed_mult - 0.25)
        elif key in (ord('c'), ord('C')):
            st['theme_idx'] = (st['theme_idx'] + 1) % len(THEME_ORDER)
            ch_.change_theme(THEME_ORDER[st['theme_idx']])
        elif key in (ord('b'), ord('B')):
            if config['style'] == 'xmas':
                for lamp in st['lamps']:
                    lamp.flame_size = (lamp.flame_size + 1) % 3
            else:
                for lamp in st['lamps']:
                    lamp.add_ball()
        elif key in (ord('v'), ord('V')):
            if config['style'] == 'xmas':
                for lamp in st['lamps']:
                    lamp.flame_size = (lamp.flame_size - 1) % 3
            else:
                for lamp in st['lamps']:
                    lamp.remove_ball()
        elif key in (ord('t'), ord('T')):
            for lamp in st['lamps']:
                lamp.trails = not lamp.trails
                if not lamp.trails:
                    lamp.trail_buffer = None
        elif key in (ord('r'), ord('R')):
            bw, bh, nb, br, bhh, chh = calculate_lamp_dims(
                st['term_w'], st['term_h'], st['lamp_count'],
                config['size'], config['style'])
            st['lamps'].clear()
            for _ in range(st['lamp_count']):
                st['lamps'].append(Lamp(config['style'], bw, bh,
                                        config['flow'], nb, br, bhh, chh,
                                        freestyle=st['is_fullscreen'],
                                        bicolor=bool(st['bicolor_theme'])))
            st['positions'] = (layout_lamps(st['lamps'], st['term_w'], st['term_h'])
                               if not st['is_fullscreen'] else [(0, 0)])
        return False

    return _run_animation(screen, deadline, ch, state,
                          _draw, _update, _draw_hud_fn, _handle_key, None)


def _run_donut(screen, config, deadline=None):
    """Run the spinning donut animation. Returns True to go back to menu, False to quit."""
    ch = ColorHelper(config['theme'])
    ch.setup()
    ch.setup_donut_colors()

    term_h, term_w = screen.getmaxyx()
    donut = Donut(term_w, term_h - 1, theme_name=config['theme'])

    state = {
        'ch': ch, 'donut': donut,
        'term_h': term_h, 'term_w': term_w,
        'theme_idx': THEME_ORDER.index(config['theme']),
    }

    def _update(st):
        st['donut'].update()

    def _draw(scr, st, ch_):
        st['donut'].render(scr, ch_)

    def _draw_hud_fn(scr, st, ch_):
        draw_donut_hud(scr, st['term_h'], st['term_w'], st['donut'], ch_)

    def _handle_key(key, st, ch_):
        if key == curses.KEY_RESIZE:
            th, tw = scr.getmaxyx()
            st['term_h'], st['term_w'] = th, tw
            st['donut'].resize(tw, th - 1)
        elif key == ord(' '):
            st['donut'].paused = not st['donut'].paused
        elif key in (ord('+'), ord('=')):
            st['donut'].speed_mult = min(3.0, st['donut'].speed_mult + 0.25)
        elif key in (ord('-'), ord('_')):
            st['donut'].speed_mult = max(0.25, st['donut'].speed_mult - 0.25)
        elif key in (ord('c'), ord('C')):
            st['theme_idx'] = (st['theme_idx'] + 1) % len(THEME_ORDER)
            ch_.change_theme(THEME_ORDER[st['theme_idx']])
            ch_.setup_donut_colors()
            st['donut'].set_theme(THEME_ORDER[st['theme_idx']])
        elif key in (ord('b'), ord('B')):
            st['donut'].next_shade()
        elif key in (ord('v'), ord('V')):
            st['donut'].prev_shade()
        elif key in (ord('r'), ord('R')):
            st['donut'] = Donut(st['term_w'], st['term_h'] - 1,
                                st['donut'].speed_mult,
                                theme_name=THEME_ORDER[st['theme_idx']])
        return False

    return _run_animation(screen, deadline, ch, state,
                          _draw, _update, _draw_hud_fn, _handle_key, None)


def _run_pond(screen, config, deadline=None):
    """Run the koi pond animation. Returns True to go back to menu, False to quit."""
    ch = ColorHelper(config['theme'])
    ch.setup()
    ch.setup_pond_colors()

    term_h, term_w = screen.getmaxyx()
    fish_count = max(3, config.get('count', 1) * 2 + 1)
    pond = Pond(term_w, term_h - 1, fish_count)

    state = {
        'ch': ch, 'pond': pond, 'fish_count': fish_count,
        'term_h': term_h, 'term_w': term_w,
        'theme_idx': THEME_ORDER.index(config['theme']),
    }

    def _update(st):
        st['pond'].update()

    def _draw(scr, st, ch_):
        st['pond'].render(scr, ch_)

    def _draw_hud_fn(scr, st, ch_):
        draw_pond_hud(scr, st['term_h'], st['term_w'], st['pond'], ch_)

    def _handle_key(key, st, ch_):
        if key == curses.KEY_RESIZE:
            th, tw = scr.getmaxyx()
            st['term_h'], st['term_w'] = th, tw
            st['pond'].resize(tw, th - 1)
        elif key == ord(' '):
            st['pond'].paused = not st['pond'].paused
        elif key in (ord('+'), ord('=')):
            st['pond'].speed_mult = min(3.0, st['pond'].speed_mult + 0.25)
        elif key in (ord('-'), ord('_')):
            st['pond'].speed_mult = max(0.25, st['pond'].speed_mult - 0.25)
        elif key in (ord('c'), ord('C')):
            st['theme_idx'] = (st['theme_idx'] + 1) % len(THEME_ORDER)
            ch_.change_theme(THEME_ORDER[st['theme_idx']])
            ch_.setup_pond_colors()
        elif key in (ord('b'), ord('B')):
            st['pond'].add_fish()
        elif key in (ord('v'), ord('V')):
            st['pond'].remove_fish()
        elif key in (ord('r'), ord('R')):
            st['pond'] = Pond(st['term_w'], st['term_h'] - 1,
                              st['fish_count'], st['pond'].speed_mult)
        return False

    return _run_animation(screen, deadline, ch, state,
                          _draw, _update, _draw_hud_fn, _handle_key, None)
