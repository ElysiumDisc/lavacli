"""Interactive selection menu for LavaCLI."""
import curses
from .lamp import SHAPE_ORDER, FLOW_ORDER, SIZE_ORDER, SIZE_NAMES
from .themes import THEMES, THEME_ORDER

TITLE = [
    '  _                     ____ _     ___  ',
    ' | |    __ ___   ____ _/ ___| |   |_ _| ',
    ' | |   / _` \\ \\ / / _` | |   | |    | |  ',
    ' | |__| (_| |\\ V / (_| | |___| |___ | |  ',
    ' |_____\\__,_| \\_/ \\__,_\\____|_____|___| ',
]

FIELDS = [
    ('STYLE', [s.capitalize() for s in SHAPE_ORDER]),
    ('THEME', [THEMES[t]['name'] for t in THEME_ORDER]),
    ('FLOW', [f.capitalize() for f in FLOW_ORDER]),
    ('COUNT', [str(i) for i in range(1, 7)]),
    ('SIZE', [SIZE_NAMES[s] for s in SIZE_ORDER]),
]


def show_menu(screen):
    """Display the interactive configuration menu. Returns config dict or None."""
    curses.curs_set(0)
    screen.clear()

    selections = [0, 0, 0, 2, 1]  # default: classic, retro_red, classic, 3 lamps, medium
    current_field = 0

    while True:
        screen.erase()
        height, width = screen.getmaxyx()

        if height < 22 or width < 50:
            screen.addstr(0, 0, 'Terminal too small. Resize to at least 50x22.')
            screen.refresh()
            screen.getch()
            continue

        # Calculate centering
        menu_width = 48
        menu_height = len(TITLE) + len(FIELDS) * 2 + 10
        start_x = max(0, (width - menu_width) // 2)
        start_y = max(0, (height - menu_height) // 2)

        # Draw title
        for i, line in enumerate(TITLE):
            try:
                x = max(0, (width - len(line)) // 2)
                screen.addstr(start_y + i, x, line, curses.A_BOLD)
            except curses.error:
                pass

        subtitle = 'Terminal Lava Lamp'
        try:
            screen.addstr(start_y + len(TITLE) + 1,
                          max(0, (width - len(subtitle)) // 2),
                          subtitle, curses.A_DIM)
        except curses.error:
            pass

        # Draw separator
        sep_y = start_y + len(TITLE) + 3
        sep = '\u2500' * min(menu_width, width - start_x - 2)
        try:
            screen.addstr(sep_y, start_x, sep, curses.A_DIM)
        except curses.error:
            pass

        # Draw fields
        field_y = sep_y + 2
        for fi, (label, options) in enumerate(FIELDS):
            y = field_y + fi * 2
            is_active = fi == current_field
            sel = selections[fi]

            # Label
            prefix = '\u25b8 ' if is_active else '  '
            label_attr = curses.A_BOLD if is_active else curses.A_DIM
            try:
                screen.addstr(y, start_x + 1, prefix + label, label_attr)
            except curses.error:
                pass

            # Options
            opt_x = start_x + 14
            for oi, opt in enumerate(options):
                is_selected = oi == sel
                if is_selected and is_active:
                    attr = curses.A_BOLD | curses.A_REVERSE
                elif is_selected:
                    attr = curses.A_BOLD
                else:
                    attr = curses.A_DIM

                # Draw arrows around selected option
                text = opt
                if is_selected:
                    text = '\u25c2 ' + opt + ' \u25b8'

                try:
                    screen.addstr(y, opt_x, text, attr)
                except curses.error:
                    pass
                opt_x += len(text) + 2

        # Launch button
        btn_y = field_y + len(FIELDS) * 2 + 1
        btn_text = '[ ENTER TO LAUNCH ]'
        is_btn = current_field == len(FIELDS)
        btn_attr = curses.A_BOLD | curses.A_REVERSE if is_btn else curses.A_BOLD
        try:
            screen.addstr(btn_y, max(0, (width - len(btn_text)) // 2), btn_text, btn_attr)
        except curses.error:
            pass

        # Controls help
        help_y = btn_y + 3
        help_text = '\u2191\u2193 Navigate   \u2190\u2192 Change   Enter Launch   Q Quit'
        try:
            screen.addstr(help_y, max(0, (width - len(help_text)) // 2), help_text, curses.A_DIM)
        except curses.error:
            pass

        screen.refresh()

        # Input
        key = screen.getch()

        if key == ord('q') or key == ord('Q') or key == 27:  # q or ESC
            return None

        elif key == curses.KEY_UP or key == ord('k'):
            current_field = max(0, current_field - 1)

        elif key == curses.KEY_DOWN or key == ord('j'):
            current_field = min(len(FIELDS), current_field + 1)

        elif key == curses.KEY_LEFT or key == ord('h'):
            if current_field < len(FIELDS):
                n = len(FIELDS[current_field][1])
                selections[current_field] = (selections[current_field] - 1) % n

        elif key == curses.KEY_RIGHT or key == ord('l'):
            if current_field < len(FIELDS):
                n = len(FIELDS[current_field][1])
                selections[current_field] = (selections[current_field] + 1) % n

        elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:
            # Launch
            return {
                'style': SHAPE_ORDER[selections[0]],
                'theme': THEME_ORDER[selections[1]],
                'flow': FLOW_ORDER[selections[2]],
                'count': selections[3] + 1,
                'size': SIZE_ORDER[selections[4]],
            }

        elif key == curses.KEY_RESIZE:
            pass  # Just re-render
