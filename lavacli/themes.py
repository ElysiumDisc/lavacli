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
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
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
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
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
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
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
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
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
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
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
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
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
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
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
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
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
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
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
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
    },
    'koi_pond': {
        'name': 'Koi Pond',
        # Watercolor pond palette: teal water, white-orange koi, sage pads
        'lava': [231, 224, 209, 202, 196],         # white -> salmon -> orange -> red
        'liquid': 30,                               # teal water (matches reference image)
        'rim': 24,                                  # darker teal glow
        'base_color': 240,
        'base_mid': 237,
        'base_shadow': 234,
        'border': 16,
        'glow': 23,
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
    },
    'aurora': {
        'name': 'Aurora',
        # Night-sky ribbons: violet -> magenta -> green -> cyan over black.
        # Pairs with the Fireplace style for a "northern lights" vibe.
        'lava': [55, 92, 35, 48, 51],              # violet -> magenta -> greens -> cyan
        'liquid': 232,                              # near-black night sky
        'rim': 93,                                  # purple halo
        'base_color': 235,
        'base_mid': 234,
        'base_shadow': 232,
        'border': 16,
        'glow': 54,
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
    },
    'campfire': {
        'name': 'Campfire',
        'lava': [88, 160, 202, 208, 220],           # dark maroon edge -> red -> orange -> golden core
        'liquid': 232,                              # black night sky
        'rim': 52,                                  # very dark maroon ember halo
        'base_color': 94,                           # brown logs
        'base_mid': 130,
        'base_shadow': 52,
        'border': 16,
        'glow': 52,
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
    },
    'cyberpunk': {
        'name': 'Cyberpunk',
        'lava': [201, 199, 51, 45, 33],             # hot pink -> cyan -> blue
        'liquid': 16,                               # black
        'rim': 127,                                 # dark purple glow
        'base_color': 240,
        'base_mid': 237,
        'base_shadow': 234,
        'border': 16,
        'glow': 53,
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
    },
    'matrix': {
        'name': 'Matrix',
        'lava': [46, 40, 34, 28, 22],               # neon green -> dark green
        'liquid': 232,                              # black
        'rim': 22,                                  # dark green glow
        'base_color': 240,
        'base_mid': 237,
        'base_shadow': 234,
        'border': 16,
        'glow': 22,
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
    },
    'oceanic': {
        'name': 'Oceanic',
        'lava': [51, 45, 39, 33, 27],               # cyan -> deep blue
        'liquid': 17,                               # dark navy
        'rim': 18,                                  # deep blue glow
        'base_color': 240,
        'base_mid': 237,
        'base_shadow': 234,
        'border': 16,
        'glow': 18,
        'lily_pad': 65, 'lily_pad_dark': 22, 'lily_pad_rim': 107,
    },
}

THEME_ORDER = [
    'yellow_red', 'blue_white', 'clear_orange', 'purple_haze',
    'neon_green', 'blue_purple', 'clear_red', 'sunset',
    'psychedelic', 'mono', 'koi_pond', 'aurora',
    'campfire', 'cyberpunk', 'matrix', 'oceanic',
]

# ---------------------------------------------------------------------------
# Koi fish color patterns (ANSI-256 color codes)
# ---------------------------------------------------------------------------
KOI_PATTERNS = {
    'kohaku': {
        'name': 'Kohaku',
        'head': 231,         # white
        'body_main': 202,    # orange-red
        'body_accent': 231,  # white patches
        'fin': 224,          # light salmon
        'tail': 209,         # salmon
    },
    'sanke': {
        'name': 'Sanke',
        'head': 231,         # white
        'body_main': 231,    # white
        'body_accent': 196,  # red patches
        'fin': 252,          # light gray
        'tail': 248,         # gray
    },
    'showa': {
        'name': 'Showa',
        'head': 196,         # red
        'body_main': 233,    # near-black
        'body_accent': 196,  # red patches
        'fin': 236,          # dark gray
        'tail': 234,         # very dark gray
    },
    'tancho': {
        'name': 'Tancho',
        'head': 196,         # red crown
        'body_main': 231,    # white
        'body_accent': 231,  # white (clean body)
        'fin': 252,          # light gray
        'tail': 248,         # gray
    },
    'ogon': {
        'name': 'Ogon',
        'head': 220,         # bright gold
        'body_main': 214,    # yellow-gold
        'body_accent': 220,  # bright gold
        'fin': 178,          # dark gold
        'tail': 172,         # bronze
    },
    'asagi': {
        'name': 'Asagi',
        'head': 110,         # light blue
        'body_main': 67,     # blue-gray
        'body_accent': 209,  # orange belly
        'fin': 103,          # muted blue
        'tail': 67,          # blue-gray
    },
}

KOI_PATTERN_NAMES = list(KOI_PATTERNS.keys())


class ColorHelper:
    """Manages curses color pairs for lamp rendering."""

    RIM_LEVEL = 6  # index for rim color in all_colors

    def __init__(self, theme_name):
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self.num_levels = len(self.theme['lava'])
        self._max_level = self.num_levels + 1  # includes rim at index 6
        self.pair_map = {}
        self._fish_pairs = {}
        self._has_256 = False
        self._next_pair_id = 1
        # Bicolor support: when a secondary theme is set, palette_id=1
        # cells resolve through _level_colors_b via lazy pair allocation.
        self._secondary_theme_name = None
        self._level_colors_a = None
        self._level_colors_b = None
        self._lazy_pair_cache = {}

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
        # Record the primary palette's colors-by-level for bicolor lookup
        self._level_colors_a = list(all_colors)

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

        # Wood logs color (brown/tan)
        curses.init_pair(pair_id, 94, -1)
        self._log_pair = pair_id
        pair_id += 1

        self._next_pair_id = pair_id

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
        self._log_pair = 3

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

    @property
    def log_attr(self):
        return curses.color_pair(self._log_pair)

    def set_secondary_theme(self, theme_name):
        """Enable bi-color rendering: palette_id=1 cells use this theme's palette.

        Pass None to disable. Safe to call repeatedly; pair allocation is lazy
        via _lazy_pair_cache so only the (fg, bg) combos actually drawn take up
        color-pair slots.
        """
        self._secondary_theme_name = theme_name
        self._lazy_pair_cache = {}
        if theme_name is None or not self._has_256:
            self._level_colors_b = None
            return
        t = THEMES[theme_name]
        lava = t['lava']
        rim = t.get('rim', lava[0])
        self._level_colors_b = [t['liquid']] + list(lava) + [rim]

    def _color_for_level(self, level, palette_id):
        """Resolve a (level, palette_id) to an ANSI-256 color code, or -1."""
        if level < 0:
            return -1
        if palette_id == 1 and self._level_colors_b is not None:
            colors = self._level_colors_b
        else:
            colors = self._level_colors_a or []
        if not colors:
            return -1
        return colors[min(level, len(colors) - 1)]

    def _lazy_color_pair(self, fg_c, bg_c):
        """Allocate (and cache) a curses pair for an arbitrary fg/bg color combo."""
        key = (fg_c, bg_c)
        pid = self._lazy_pair_cache.get(key)
        if pid is None:
            if self._next_pair_id >= max(1, curses.COLOR_PAIRS - 1):
                # Out of color-pair slots; fall back to an existing neutral pair.
                return curses.color_pair(self.pair_map.get((0, 0), 1))
            try:
                curses.init_pair(self._next_pair_id, fg_c, bg_c)
            except curses.error:
                return curses.color_pair(self.pair_map.get((0, 0), 1))
            pid = self._next_pair_id
            self._lazy_pair_cache[key] = pid
            self._next_pair_id += 1
        return curses.color_pair(pid)

    def draw_cell(self, screen, row, col, top_level, bot_level,
                  top_pid=0, bot_pid=0):
        """Draw a half-block cell for the lamp body.
        Level: -1=outside, 0=liquid, 1+=lava intensity.
        palette_id: 0=primary theme, 1=secondary (bicolor) theme.
        """
        if top_level == -1 and bot_level == -1:
            return
        # Bicolor path: only when a secondary palette is active AND this cell
        # actually involves it. Otherwise take the fast path via pair_map.
        bicolor = (self._level_colors_b is not None
                   and (top_pid == 1 or bot_pid == 1))
        try:
            if bicolor:
                top_c = self._color_for_level(top_level, top_pid)
                bot_c = self._color_for_level(bot_level, bot_pid)
                if top_level == -1:
                    screen.addstr(row, col, '\u2584',
                                  self._lazy_color_pair(bot_c, -1))
                elif bot_level == -1:
                    screen.addstr(row, col, '\u2580',
                                  self._lazy_color_pair(top_c, -1))
                else:
                    screen.addstr(row, col, '\u2580',
                                  self._lazy_color_pair(top_c, bot_c))
                return
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

    def setup_pond_colors(self):
        """Allocate color pairs for koi pond rendering. Call after setup()."""
        if not self._has_256:
            self._setup_pond_basic()
            return

        water = self.theme['liquid']
        self._water_color = water

        # Count existing pairs to find next available ID
        pair_id = self._next_pair_id

        # Water-on-water (background)
        curses.init_pair(pair_id, water, water)
        self._water_pair = pair_id
        pair_id += 1

        # Collect all unique fish colors (plus lily pad colors)
        fish_colors = set()
        for pattern in KOI_PATTERNS.values():
            for part in ('head', 'body_main', 'body_accent', 'fin', 'tail'):
                fish_colors.add(pattern[part])
        # Lily pad colors share the _fish_pairs machinery so they
        # render through draw_pond_cell with no extra plumbing
        fish_colors.add(self.theme.get('lily_pad', 65))
        fish_colors.add(self.theme.get('lily_pad_dark', 22))
        fish_colors.add(self.theme.get('lily_pad_rim', 107))

        self._fish_pairs = {}
        for color in sorted(fish_colors):
            # fish as fg, water as bg
            curses.init_pair(pair_id, color, water)
            self._fish_pairs[(color, 'fg')] = pair_id
            pair_id += 1
            # water as fg, fish as bg
            curses.init_pair(pair_id, water, color)
            self._fish_pairs[(color, 'bg')] = pair_id
            pair_id += 1
            # fish on fish (same color) - full block
            curses.init_pair(pair_id, color, color)
            self._fish_pairs[(color, 'full')] = pair_id
            pair_id += 1

        # Cross-fish pairs for two different fish colors in same cell
        # Pre-allocate for all unique (fg, bg) combos among fish colors
        color_list = sorted(fish_colors)
        for fg in color_list:
            for bg in color_list:
                if fg != bg and (fg, bg) not in self._fish_pairs:
                    curses.init_pair(pair_id, fg, bg)
                    self._fish_pairs[(fg, bg)] = pair_id
                    pair_id += 1

        self._next_pair_id = pair_id

    def _setup_pond_basic(self):
        """Fallback pond colors for 8-color terminals."""
        self._water_pair = 4  # white on blue
        self._fish_pairs = {}

    def draw_pond_cell(self, screen, row, col, top_cell, bot_cell):
        """Draw a half-block cell for the pond.
        cell is None (water) or (pattern_name, segment_idx, dist_from_center).
        """
        top_color = self._resolve_fish_color(top_cell)
        bot_color = self._resolve_fish_color(bot_cell)

        try:
            if top_color is None and bot_color is None:
                # Both water
                screen.addstr(row, col, ' ',
                              curses.color_pair(self._water_pair))
            elif top_color is None:
                # Top water, bottom fish: ▄ with fg=fish, bg=water
                pid = self._fish_pairs.get((bot_color, 'bg'),
                                           self._water_pair)
                screen.addstr(row, col, '\u2584', curses.color_pair(pid))
            elif bot_color is None:
                # Top fish, bottom water: ▀ with fg=fish, bg=water
                pid = self._fish_pairs.get((top_color, 'fg'),
                                           self._water_pair)
                screen.addstr(row, col, '\u2580', curses.color_pair(pid))
            elif top_color == bot_color:
                # Same fish color: full block
                pid = self._fish_pairs.get((top_color, 'full'),
                                           self._fish_pairs.get(
                                               (top_color, 'fg'),
                                               self._water_pair))
                screen.addstr(row, col, '\u2588', curses.color_pair(pid))
            else:
                # Two different fish colors: ▀ fg=top, bg=bottom
                pid = self._fish_pairs.get((top_color, bot_color),
                                           self._water_pair)
                screen.addstr(row, col, '\u2580', curses.color_pair(pid))
        except curses.error:
            pass

    def _resolve_fish_color(self, cell):
        """Map a buffer cell to an ANSI-256 color code, or None for water.

        Cell shapes:
            None                       -> water
            ('pad', shade)             -> lily pad (shade in 'rim'/'fill'/'shadow')
            (pattern_name, seg_idx, d) -> fish segment
        """
        if cell is None:
            return None
        # Lily pad cell
        if cell[0] == 'pad':
            shade = cell[1]
            if shade == 'rim':
                return self.theme.get('lily_pad_rim', 107)
            elif shade == 'shadow':
                return self.theme.get('lily_pad_dark', 22)
            return self.theme.get('lily_pad', 65)
        # Fish cell
        pattern_name, seg_idx, dist = cell
        pattern = KOI_PATTERNS[pattern_name]
        # 14-segment body: 0=snout, 1=head, 2-9=body, 10-11=peduncle, 12-13=tail
        if seg_idx <= 1:
            return pattern['head']
        elif seg_idx >= 12:
            return pattern['tail']
        elif seg_idx in (4, 5) and dist > 0.6:
            return pattern['fin']
        elif seg_idx >= 10:
            # Caudal peduncle: use body_main (thin section before tail)
            return pattern['body_main']
        else:
            # Body: alternate main/accent for patchy koi markings
            if seg_idx % 3 == 0:
                return pattern['body_accent']
            return pattern['body_main']

    def setup_donut_colors(self):
        """Pre-allocate curses pairs for every theme's lava palette against
        the current primary liquid color, plus solid (c, c) pairs. Keeps
        donut sprinkles from silently falling back to the (liquid, liquid)
        pair when lazy allocation can't get a new slot mid-render.
        """
        if not self._has_256:
            return
        liquid = self.theme['liquid']
        colors = set()
        for theme in THEMES.values():
            for c in theme['lava']:
                colors.add(c)
        for c in sorted(colors):
            self._lazy_color_pair(c, liquid)
            self._lazy_color_pair(c, c)

    def draw_colored_cell(self, screen, row, col, top_color, bot_color):
        """Draw a half-block pair with arbitrary ANSI-256 colors.

        top_color/bot_color: an ANSI color code, or None to use the current
        theme's liquid color as the background fill. Used by the donut
        renderer so each sprinkle can come from a different theme palette
        while the torus sits on the primary theme's liquid backdrop.
        """
        liquid = self.theme['liquid']
        tc = liquid if top_color is None else top_color
        bc = liquid if bot_color is None else bot_color
        try:
            if tc == bc:
                screen.addstr(row, col, '\u2588',
                              self._lazy_color_pair(tc, tc))
            else:
                screen.addstr(row, col, '\u2580',
                              self._lazy_color_pair(tc, bc))
        except curses.error:
            pass

    def change_theme(self, theme_name):
        """Switch to a different theme (keeping secondary bicolor theme if set)."""
        self.theme_name = theme_name
        self.theme = THEMES[theme_name]
        self.num_levels = len(self.theme['lava'])
        self.pair_map.clear()
        self._fish_pairs = {}
        self._lazy_pair_cache = {}
        self.setup()
        # Re-apply secondary palette (setup resets _level_colors_a)
        if self._secondary_theme_name is not None:
            self.set_secondary_theme(self._secondary_theme_name)
