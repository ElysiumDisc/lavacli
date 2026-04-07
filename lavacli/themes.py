"""Color themes and rendering helper for LavaCLI."""
import curses

THEMES = {
    'retro_red': {
        'name': 'Retro Red',
        'lava': [196, 202, 208, 214, 220],
        'glass': 234,
        'border': 245,
        'base': 240,
        'glow': 52,
    },
    'ocean': {
        'name': 'Ocean Blue',
        'lava': [21, 27, 33, 39, 51],
        'glass': 234,
        'border': 245,
        'base': 240,
        'glow': 17,
    },
    'neon': {
        'name': 'Neon Green',
        'lava': [22, 28, 34, 40, 46],
        'glass': 234,
        'border': 245,
        'base': 240,
        'glow': 22,
    },
    'sunset': {
        'name': 'Sunset',
        'lava': [160, 196, 202, 208, 214],
        'glass': 234,
        'border': 245,
        'base': 240,
        'glow': 52,
    },
    'purple': {
        'name': 'Purple Haze',
        'lava': [54, 92, 129, 135, 177],
        'glass': 234,
        'border': 245,
        'base': 240,
        'glow': 53,
    },
    'psychedelic': {
        'name': 'Psychedelic',
        'lava': [196, 226, 46, 51, 201],
        'glass': 234,
        'border': 245,
        'base': 240,
        'glow': 0,
    },
    'mono': {
        'name': 'Monochrome',
        'lava': [240, 244, 248, 252, 255],
        'glass': 234,
        'border': 245,
        'base': 240,
        'glow': 238,
    },
}

THEME_ORDER = ['retro_red', 'ocean', 'neon', 'sunset', 'purple', 'psychedelic', 'mono']


class ColorHelper:
    """Manages curses color pairs for lamp rendering."""

    def __init__(self, theme_name):
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self.num_levels = len(self.theme['lava'])
        self.pair_map = {}
        self.border_pair_id = 0
        self.base_pair_id = 0
        self.text_pair_id = 0
        self.highlight_pair_id = 0
        self.glow_pair_id = 0
        self._has_256 = False

    def setup(self):
        """Initialize curses color pairs. Call after curses.initscr()."""
        curses.start_color()
        curses.use_default_colors()
        self._has_256 = curses.COLORS >= 256

        if not self._has_256:
            self._setup_basic()
            return

        t = self.theme
        glass = t['glass']
        lava = t['lava']
        n = self.num_levels + 1  # index 0 = glass, 1..n = lava levels

        all_colors = [glass] + list(lava)

        pair_id = 1
        for i in range(n):
            for j in range(n):
                curses.init_pair(pair_id, all_colors[i], all_colors[j])
                self.pair_map[(i, j)] = pair_id
                pair_id += 1

        # Lava on default bg (for outside-glass edges)
        for i in range(n):
            curses.init_pair(pair_id, all_colors[i], -1)
            self.pair_map[(i, -1)] = pair_id
            pair_id += 1
            curses.init_pair(pair_id, -1, all_colors[i])
            self.pair_map[(-1, i)] = pair_id
            pair_id += 1

        curses.init_pair(pair_id, t['border'], -1)
        self.border_pair_id = pair_id
        pair_id += 1

        curses.init_pair(pair_id, t['base'], -1)
        self.base_pair_id = pair_id
        pair_id += 1

        curses.init_pair(pair_id, t['glow'], -1)
        self.glow_pair_id = pair_id
        pair_id += 1

        curses.init_pair(pair_id, curses.COLOR_WHITE, -1)
        self.text_pair_id = pair_id
        pair_id += 1

        curses.init_pair(pair_id, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.highlight_pair_id = pair_id
        pair_id += 1

        # Menu selection colors
        curses.init_pair(pair_id, lava[2], -1)
        self.menu_accent_id = pair_id
        pair_id += 1

        curses.init_pair(pair_id, 243, -1)
        self.menu_dim_id = pair_id
        pair_id += 1

    def _setup_basic(self):
        """Fallback for 8-color terminals."""
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.pair_map[(0, 0)] = 3
        for i in range(1, self.num_levels + 1):
            self.pair_map[(i, 0)] = 1
            self.pair_map[(0, i)] = 1
            for j in range(1, self.num_levels + 1):
                self.pair_map[(i, j)] = 2
        self.border_pair_id = 3
        self.base_pair_id = 3
        self.text_pair_id = 3
        self.highlight_pair_id = 3
        self.glow_pair_id = 1
        self.menu_accent_id = 2
        self.menu_dim_id = 3

    def get_pair(self, fg_level, bg_level):
        """Get curses color_pair attr for fg/bg level combo.
        Level: 0=glass, 1-5=lava intensity, -1=default bg."""
        fg = max(-1, min(fg_level, self.num_levels))
        bg = max(-1, min(bg_level, self.num_levels))
        pid = self.pair_map.get((fg, bg), self.pair_map.get((0, 0), 1))
        return curses.color_pair(pid)

    @property
    def border_attr(self):
        return curses.color_pair(self.border_pair_id)

    @property
    def base_attr(self):
        return curses.color_pair(self.base_pair_id)

    @property
    def glow_attr(self):
        return curses.color_pair(self.glow_pair_id)

    @property
    def text_attr(self):
        return curses.color_pair(self.text_pair_id)

    @property
    def highlight_attr(self):
        return curses.color_pair(self.highlight_pair_id)

    @property
    def accent_attr(self):
        return curses.color_pair(self.menu_accent_id)

    @property
    def dim_attr(self):
        return curses.color_pair(self.menu_dim_id)

    def draw_cell(self, screen, row, col, top_level, bot_level):
        """Draw a half-block cell. Level: -1=outside, 0=glass, 1+=lava."""
        try:
            if top_level <= 0 and bot_level <= 0:
                if top_level == 0 or bot_level == 0:
                    screen.addstr(row, col, ' ', self.get_pair(0, 0))
            elif top_level > 0 and bot_level > 0:
                screen.addstr(row, col, '\u2580', self.get_pair(top_level, bot_level))
            elif top_level > 0:
                bg = 0 if bot_level == 0 else -1
                screen.addstr(row, col, '\u2580', self.get_pair(top_level, bg))
            else:
                bg = 0 if top_level == 0 else -1
                screen.addstr(row, col, '\u2584', self.get_pair(bot_level, bg))
        except curses.error:
            pass

    def change_theme(self, theme_name):
        """Switch to a different theme."""
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self.pair_map.clear()
        self.setup()
