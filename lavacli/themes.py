"""Color themes and rendering helper for LavaCLI."""
import curses

# Themes with colored liquid backgrounds (like real lava lamps!)
THEMES = {
    'retro_red': {
        'name': 'Retro Red',
        'lava': [160, 196, 202, 208, 214],       # deep red -> orange -> yellow
        'liquid': 53,                              # dark purple liquid
        'base_color': 249,                         # light silver
        'base_shadow': 243,                        # darker silver
        'border': 96,                              # subtle purple border
        'glow': 52,
    },
    'ocean': {
        'name': 'Ocean Blue',
        'lava': [231, 195, 159, 123, 87],          # white -> light blue
        'liquid': 17,                              # deep navy liquid
        'base_color': 249,
        'base_shadow': 243,
        'border': 24,
        'glow': 17,
    },
    'neon': {
        'name': 'Neon Green',
        'lava': [46, 47, 48, 49, 50],             # bright green -> cyan
        'liquid': 22,                              # dark forest green liquid
        'base_color': 249,
        'base_shadow': 243,
        'border': 28,
        'glow': 22,
    },
    'sunset': {
        'name': 'Sunset',
        'lava': [196, 202, 208, 214, 220],        # red -> orange -> yellow
        'liquid': 52,                              # dark red/maroon liquid
        'base_color': 249,
        'base_shadow': 243,
        'border': 94,
        'glow': 52,
    },
    'purple': {
        'name': 'Purple Haze',
        'lava': [199, 205, 206, 207, 213],        # hot pink -> light pink
        'liquid': 54,                              # dark purple liquid
        'base_color': 249,
        'base_shadow': 243,
        'border': 96,
        'glow': 53,
    },
    'psychedelic': {
        'name': 'Psychedelic',
        'lava': [196, 226, 46, 51, 201],          # rainbow
        'liquid': 17,                              # dark navy
        'base_color': 249,
        'base_shadow': 243,
        'border': 60,
        'glow': 0,
    },
    'mono': {
        'name': 'Monochrome',
        'lava': [240, 244, 248, 252, 255],        # gray -> white
        'liquid': 233,                             # almost black
        'base_color': 249,
        'base_shadow': 243,
        'border': 238,
        'glow': 236,
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
        liquid = t['liquid']
        lava = t['lava']
        n = self.num_levels + 1  # index 0 = liquid, 1..n = lava levels

        # All renderable colors: index 0 = liquid, 1-5 = lava levels
        all_colors = [liquid] + list(lava)

        pair_id = 1

        # All (fg, bg) combos for visible colors
        for i in range(n):
            for j in range(n):
                curses.init_pair(pair_id, all_colors[i], all_colors[j])
                self.pair_map[(i, j)] = pair_id
                pair_id += 1

        # Visible color on default terminal bg (for shape edges)
        for i in range(n):
            curses.init_pair(pair_id, all_colors[i], -1)
            self.pair_map[(i, -1)] = pair_id
            pair_id += 1
            curses.init_pair(pair_id, -1, all_colors[i])
            self.pair_map[(-1, i)] = pair_id
            pair_id += 1

        # Base/cap metallic colors
        curses.init_pair(pair_id, t['base_color'], -1)
        self._base_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, t['base_shadow'], -1)
        self._base_shadow_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, t['base_color'], t['base_shadow'])
        self._base_gradient_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, t['base_shadow'], t['base_color'])
        self._base_gradient_rev_pair = pair_id
        pair_id += 1

        # Border
        curses.init_pair(pair_id, t['border'], -1)
        self._border_pair = pair_id
        pair_id += 1

        # Text and UI
        curses.init_pair(pair_id, curses.COLOR_WHITE, -1)
        self._text_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self._highlight_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, lava[2], -1)
        self._accent_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, 243, -1)
        self._dim_pair = pair_id
        pair_id += 1

    def _setup_basic(self):
        """Fallback for 8-color terminals."""
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLUE)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self.pair_map[(0, 0)] = 4
        for i in range(1, self.num_levels + 1):
            self.pair_map[(i, 0)] = 1
            self.pair_map[(0, i)] = 1
            self.pair_map[(i, -1)] = 1
            for j in range(1, self.num_levels + 1):
                self.pair_map[(i, j)] = 2
        self.pair_map[(0, -1)] = 4
        self._base_pair = 3
        self._base_shadow_pair = 3
        self._base_gradient_pair = 3
        self._base_gradient_rev_pair = 3
        self._border_pair = 3
        self._text_pair = 3
        self._highlight_pair = 3
        self._accent_pair = 1
        self._dim_pair = 3

    def get_pair(self, fg_level, bg_level):
        """Get curses color_pair attr. Level: -1=default, 0=liquid, 1-5=lava."""
        fg = max(-1, min(fg_level, self.num_levels))
        bg = max(-1, min(bg_level, self.num_levels))
        pid = self.pair_map.get((fg, bg), self.pair_map.get((0, 0), 1))
        return curses.color_pair(pid)

    @property
    def base_attr(self):
        return curses.color_pair(self._base_pair)

    @property
    def base_shadow_attr(self):
        return curses.color_pair(self._base_shadow_pair)

    @property
    def base_gradient_attr(self):
        return curses.color_pair(self._base_gradient_pair)

    @property
    def base_gradient_rev_attr(self):
        return curses.color_pair(self._base_gradient_rev_pair)

    @property
    def border_attr(self):
        return curses.color_pair(self._border_pair)

    @property
    def text_attr(self):
        return curses.color_pair(self._text_pair)

    @property
    def highlight_attr(self):
        return curses.color_pair(self._highlight_pair)

    @property
    def accent_attr(self):
        return curses.color_pair(self._accent_pair)

    @property
    def dim_attr(self):
        return curses.color_pair(self._dim_pair)

    def draw_cell(self, screen, row, col, top_level, bot_level):
        """Draw a half-block cell for the lamp body.
        Level: -1=outside, 0=liquid, 1+=lava intensity."""
        if top_level == -1 and bot_level == -1:
            return
        try:
            if top_level == -1:
                # Top outside, bottom visible
                screen.addstr(row, col, '\u2584', self.get_pair(bot_level, -1))
            elif bot_level == -1:
                # Top visible, bottom outside
                screen.addstr(row, col, '\u2580', self.get_pair(top_level, -1))
            else:
                # Both visible - use ▀ with fg=top, bg=bottom
                screen.addstr(row, col, '\u2580', self.get_pair(top_level, bot_level))
        except curses.error:
            pass

    def draw_base_cell(self, screen, row, col, top_in, bot_in, highlight=False):
        """Draw a half-block cell for the metallic base/cap."""
        if not top_in and not bot_in:
            return
        attr = self.base_attr if highlight else self.base_shadow_attr
        try:
            if top_in and bot_in:
                screen.addstr(row, col, '\u2588', attr)
            elif top_in:
                screen.addstr(row, col, '\u2580', attr)
            else:
                screen.addstr(row, col, '\u2584', attr)
        except curses.error:
            pass

    def change_theme(self, theme_name):
        """Switch to a different theme."""
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self.pair_map.clear()
        self.setup()
