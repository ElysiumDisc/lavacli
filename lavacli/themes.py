"""Color themes and rendering helper for LavaCLI."""
import curses

# Themes inspired by the classic 1992-2004 Lava Library color codes
# Black bases like real lamps, dark glass outlines for pixel-art look
THEMES = {
    'yellow_red': {
        'name': 'Yellow Red',                      # Lava Library #02
        'lava': [160, 196, 202, 208, 214],         # deep red -> orange -> yellow
        'liquid': 226,                              # yellow liquid (clear yellow)
        'rim': 88,                                  # dark red glow edge
        'base_color': 240,                          # dark gray (black base)
        'base_mid': 237,                            # darker gray
        'base_shadow': 234,                         # near black
        'border': 16,                               # black outline
        'glow': 52,
    },
    'blue_white': {
        'name': 'Blue White',                        # Lava Library #03
        'lava': [231, 195, 159, 123, 87],           # white -> light blue
        'liquid': 21,                               # blue liquid
        'rim': 25,                                  # medium navy glow
        'base_color': 240,
        'base_mid': 237,
        'base_shadow': 234,
        'border': 16,
        'glow': 17,
    },
    'clear_orange': {
        'name': 'Clear Orange',                      # Lava Library #15
        'lava': [208, 209, 214, 215, 220],          # orange -> gold -> yellow
        'liquid': 232,                              # clear/black liquid
        'rim': 130,                                 # dark orange glow
        'base_color': 240,
        'base_mid': 237,
        'base_shadow': 234,
        'border': 16,
        'glow': 94,
    },
    'purple_haze': {
        'name': 'Purple Haze',                       # Lava Library #09
        'lava': [199, 205, 206, 207, 213],          # hot pink -> light pink
        'liquid': 54,                               # dark purple liquid
        'rim': 127,                                 # medium magenta glow
        'base_color': 240,
        'base_mid': 237,
        'base_shadow': 234,
        'border': 16,
        'glow': 53,
    },
    'neon_green': {
        'name': 'Neon Green',                        # Lava Library #12
        'lava': [46, 47, 48, 49, 50],              # bright green -> cyan
        'liquid': 22,                               # dark forest green liquid
        'rim': 34,                                  # medium green glow
        'base_color': 240,
        'base_mid': 237,
        'base_shadow': 234,
        'border': 16,
        'glow': 22,
    },
    'blue_purple': {
        'name': 'Blue Purple',                       # Lava Library #22
        'lava': [129, 134, 140, 146, 183],          # purple -> lavender
        'liquid': 19,                               # deep blue liquid
        'rim': 55,                                  # dark violet glow
        'base_color': 240,
        'base_mid': 237,
        'base_shadow': 234,
        'border': 16,
        'glow': 18,
    },
    'clear_red': {
        'name': 'Clear Red',                         # Lava Library #10
        'lava': [196, 197, 203, 209, 210],          # bright red -> rose
        'liquid': 232,                              # clear/black liquid
        'rim': 52,                                  # dark red glow
        'base_color': 240,
        'base_mid': 237,
        'base_shadow': 234,
        'border': 16,
        'glow': 88,
    },
    'sunset': {
        'name': 'Sunset',
        'lava': [196, 202, 208, 214, 220],          # red -> orange -> yellow
        'liquid': 52,                               # dark red/maroon liquid
        'rim': 130,                                 # dark orange glow
        'base_color': 240,
        'base_mid': 237,
        'base_shadow': 234,
        'border': 16,
        'glow': 52,
    },
    'psychedelic': {
        'name': 'Psychedelic',
        'lava': [196, 226, 46, 51, 201],            # rainbow
        'liquid': 17,                               # dark navy
        'rim': 57,                                  # medium purple glow
        'base_color': 240,
        'base_mid': 237,
        'base_shadow': 234,
        'border': 16,
        'glow': 0,
    },
    'mono': {
        'name': 'Monochrome',
        'lava': [240, 244, 248, 252, 255],          # gray -> white
        'liquid': 233,                              # almost black
        'rim': 237,                                 # dark gray glow
        'base_color': 249,                          # silver base (classic silver variant)
        'base_mid': 246,
        'base_shadow': 243,
        'border': 236,
        'glow': 236,
    },
}

THEME_ORDER = [
    'yellow_red', 'blue_white', 'clear_orange', 'purple_haze',
    'neon_green', 'blue_purple', 'clear_red', 'sunset',
    'psychedelic', 'mono',
]


class ColorHelper:
    """Manages curses color pairs for lamp rendering."""

    RIM_LEVEL = 6  # index for rim color in all_colors

    def __init__(self, theme_name):
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self.num_levels = len(self.theme['lava'])
        self._max_level = self.num_levels + 1  # includes rim at index 6
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
        rim = t.get('rim', lava[0])

        # All renderable colors: 0=liquid, 1-5=lava, 6=rim
        all_colors = [liquid] + list(lava) + [rim]
        n = len(all_colors)
        self._max_level = n - 1

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

        # Base/cap metallic colors (3-tone: highlight, mid, shadow)
        base_hi = t['base_color']
        base_mid = t.get('base_mid', 246)
        base_sh = t['base_shadow']

        curses.init_pair(pair_id, base_hi, -1)
        self._base_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, base_mid, -1)
        self._base_mid_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, base_sh, -1)
        self._base_shadow_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, base_hi, base_sh)
        self._base_gradient_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, base_sh, base_hi)
        self._base_gradient_rev_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, base_hi, base_mid)
        self._base_hi_mid_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, base_mid, base_hi)
        self._base_mid_hi_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, base_mid, base_sh)
        self._base_mid_sh_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, base_sh, base_mid)
        self._base_sh_mid_pair = pair_id
        pair_id += 1

        # Border / glass frame outline
        border_c = t['border']
        curses.init_pair(pair_id, border_c, -1)
        self._border_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, border_c, border_c)
        self._border_full_pair = pair_id
        pair_id += 1

        curses.init_pair(pair_id, -1, border_c)
        self._border_bg_pair = pair_id
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
        # Rim level (6) maps same as other lava levels in basic mode
        self.pair_map[(6, 0)] = 1
        self.pair_map[(0, 6)] = 1
        self.pair_map[(6, -1)] = 1
        for j in range(1, self.num_levels + 1):
            self.pair_map[(6, j)] = 2
            self.pair_map[(j, 6)] = 2
        self.pair_map[(6, 6)] = 2
        self.pair_map[(0, -1)] = 4
        self._base_pair = 3
        self._base_mid_pair = 3
        self._base_shadow_pair = 3
        self._base_gradient_pair = 3
        self._base_gradient_rev_pair = 3
        self._base_hi_mid_pair = 3
        self._base_mid_hi_pair = 3
        self._base_mid_sh_pair = 3
        self._base_sh_mid_pair = 3
        self._border_pair = 3
        self._border_full_pair = 3
        self._border_bg_pair = 3
        self._text_pair = 3
        self._highlight_pair = 3
        self._accent_pair = 1
        self._dim_pair = 3

    def get_pair(self, fg_level, bg_level):
        """Get curses color_pair attr. Level: -1=default, 0=liquid, 1-5=lava, 6=rim."""
        fg = max(-1, min(fg_level, self._max_level))
        bg = max(-1, min(bg_level, self._max_level))
        pid = self.pair_map.get((fg, bg), self.pair_map.get((0, 0), 1))
        return curses.color_pair(pid)

    @property
    def base_attr(self):
        return curses.color_pair(self._base_pair)

    @property
    def base_mid_attr(self):
        return curses.color_pair(self._base_mid_pair)

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

    def get_base_shade_attr(self, shade):
        """Get metallic shade attr. shade: 'hi', 'mid', or 'sh'."""
        if shade == 'hi':
            return self.base_attr
        elif shade == 'mid':
            return self.base_mid_attr
        else:
            return self.base_shadow_attr

    def draw_base_cell(self, screen, row, col, top_in, bot_in,
                       highlight=False, shade=None):
        """Draw a half-block cell for the metallic base/cap.
        shade: 'hi'/'mid'/'sh' for 3-tone, or None to use highlight bool."""
        if not top_in and not bot_in:
            return
        if shade is not None:
            attr = self.get_base_shade_attr(shade)
        else:
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

    def draw_frame_cell(self, screen, row, col, top_in, bot_in):
        """Draw a half-block cell for the glass frame outline (dark border)."""
        if not top_in and not bot_in:
            return
        attr = curses.color_pair(self._border_full_pair)
        try:
            if top_in and bot_in:
                screen.addstr(row, col, '\u2588', attr)
            elif top_in:
                screen.addstr(row, col, '\u2580', self.border_attr)
            else:
                screen.addstr(row, col, '\u2584', self.border_attr)
        except curses.error:
            pass

    def change_theme(self, theme_name):
        """Switch to a different theme."""
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self.num_levels = len(self.theme['lava'])
        self.pair_map.clear()
        self.setup()
