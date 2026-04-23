# Changelog

All notable changes to LavaCLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.6.0] - 2026-04-22

### Added
- **4 New Themes** - Cyberpunk (neon pink/cyan), Matrix (hacker greens), Oceanic (deep sea blues), and Campfire (cozy golden core through orange and red to dark ember glow at the edges, over a black night sky).
- **Procedural 3D Campfire Logs & Pine Forest** - The `fireplace` style now features a high-fidelity, procedurally generated log structure at the base. Includes 3D-shaded bark textures, concentric wood rings on log ends, glowing cracks/embers, and a scattered ash bed. The **Campfire theme** renders a layered **pine tree silhouette background** with rolling hills and a starry night sky.
- **Warm Firelight Glow on Forest Floor** - A radial amber/orange-brown glow emanates from the campfire center onto the forest floor, simulating warm light cast by the flames.
- **Licking Flame Animation** - Upgraded the fire animation with teardrop-shaped embers and sine-wave "licking" motion for the flame tails, creating an organic waving effect.
- **Sustained Flame Core** - Added a solid, swaying procedural flame pillar that emerges from the logs, providing a continuous core of fire.
- **Flame Shaping** - Revised ember temperature model forms a natural, triangular flame shape by cooling side embers faster than those in the center.

### Changed
- **Campfire palette corrected** - Flame colors now flow from dark maroon at the outer ember glow through red → orange → warm orange → golden yellow at the hottest center, matching how real fire looks (previously the gradient was inverted).
- **Wider campfire ember spawn** - Embers now spawn with an 8% Gaussian spread (was 4%), giving the fire a fuller, more natural base that matches the log width.
- **`ColorHelper` composite rendering** - Integrated procedural log and forest rendering into the half-block pipeline with true color compositing.


## [1.5.0] - 2026-04-13

### Added

- **Donut mode** - New 12th lamp style: a fullscreen spinning ASCII donut, ported from Andy Sloane's classic donut.c. The torus (R1=1, R2=2) rotates about two axes with perspective projection and Lambertian lighting, rasterized via the app's half-block pipeline so it composes with the existing theme/HUD/resize machinery. Sized so its projected diameter spans 70-85% of each terminal axis — a proper BIG SPINNING DONUT rather than a min-dim-capped miniature
- **Theme-cycling sprinkles** - Instead of donut.c's 12-character luminance ramp, each lit point on the torus picks its palette from `THEME_ORDER` and the Lambertian intensity picks the shade within that palette, so the donut is rendered entirely out of theme colors. A time offset rotates the selection every few frames, so the whole donut visibly cycles through all 12 themes as it spins
- **8 sprinkle patterns** - `B`/`V` during donut mode cycle the spatial component of the palette selection. Default `(0, 0)` is "solid" — whole donut shares one palette that shifts through every theme over time (clearest theme-cycling look). Other patterns layer in ring bands `(1, 3)`, tube stripes `(5, 1)`, broad wraps `(1, 7)`, diagonal confetti `(3, 5)`, chunky wedges `(0, 1)`, stacked hoops `(1, 0)`, and fine speckle `(7, 7)`
- **`ColorHelper.setup_donut_colors()`** - Pre-warms a curses color pair for every `(lava_color, liquid_bg)` and `(lava_color, lava_color)` combo across all 12 theme palettes (~120 pairs). Without this pre-allocation, `_lazy_color_pair` can silently fall back to the `(liquid, liquid)` pair mid-render when it runs out of slots — which was making sprinkles disappear
- **`ColorHelper.draw_colored_cell()`** - Generic half-block draw helper that accepts arbitrary ANSI-256 colors for the top and bottom cell halves, backed by the lazy pair cache. Used by the donut renderer so sprinkles from many themes can coexist on the same frame
- **Live donut preview in the menu** - Hovering "Donut" in the STYLE menu now renders a real miniature spinning donut in the preview panel, right next to the Koi Pond preview

### Changed

- **Sampling density** - Donut inner-loop steps match donut.c's originals (`θ=0.07`, `φ=0.02`), ~28k sample points per frame. Python sustains ~40 fps on a default terminal thanks to the flat buffer + integer palette index math
- **Width and height scale independently** - Earlier draft capped the donut on `min(w, ph)`, leaving tiny donuts on wide terminals. Now `scale_x = w * 0.58` and `scale_y = ph * 0.58` give a big ring on any aspect ratio

## [1.4.0] - 2026-04-12

### Added

- **Fireplace mode** - New 11th lamp style: a fullscreen crackling fireplace of rising embers. Reuses the metaball engine with inverted physics — embers spawn hot at the bottom, drift upward with flicker jitter and a slight updraft curl, cool monotonically as they rise, and recycle back to the bottom once they fade. Ember brightness is driven by `ball.temp` scaling the metaball field contribution, so fading embers naturally dim through the rim level before winking out. Pairs beautifully with the Sunset, Clear Red, and new Aurora themes
- **Aurora theme** - New 12th color theme: violet → magenta → green → cyan ribbons over a near-black night sky, with a purple halo glow and a dark metal base. Designed as the companion theme to Fireplace, but looks great on any fullscreen or glass lamp
- **Bi-color lava** (`--bicolor THEME_B` flag, `TINT` menu field) - A single lamp can now mix two palettes like the 90s red/blue Mathmos bi-color lamps. Half the blobs carry the primary theme's palette, half carry the secondary's. Color pairs for cross-palette combos are lazily allocated via a new `ColorHelper.set_secondary_theme` / `_lazy_color_pair` pathway, so only the (fg, bg) combos actually drawn consume curses pair slots. `B`/`V` during animation keeps the two palettes balanced
- **Blob trails** (`T` key) - Toggle a "slow-shutter" motion-blur effect during animation. Each cell that has lava is remembered in a per-lamp trail buffer for ~14 frames and then fades through lower lava levels down to the rim glow before disappearing — so every blob paints a soft comet-tail behind it. Works for both glass lamps and fullscreen styles (Freestyle, Fireplace). HUD shows `T:Trails*` while active
- **Menu `TINT` field** - New 6th menu row cycling through `Off` + all 12 themes. Selecting a tint flips the live preview panel into bi-color mode instantly. Number-key jumps now go `1`–`6` to cover the new field
- **`[A+B]` HUD marker** - Displayed in the bottom controls bar whenever bi-color is active so you can tell at a glance that two palettes are mixing

### Changed

- **Menu help line updated** to reflect the new `1-6 Jump` range
- **`Lamp` constructor** accepts an optional `bicolor=False` argument. When true, each ball is assigned `palette_id = i % 2` round-robin so the two palettes are evenly distributed from the start
- **`Ball.__slots__` gained `palette_id`** so every ball carries its palette identity without a dict lookup
- **Fireplace style overrides the user-picked flow** internally (forcing its own `fireplace` physics params) because ember behavior shouldn't depend on whether the user chose Zen or Chaotic

### Fixed

- **Resize during trails / bi-color no longer leaves stale buffer entries** - `Lamp.resize` now invalidates `trail_buffer` so the next frame reallocates at the new dimensions instead of indexing into a wrong-sized 2D list

## [1.3.0] - 2026-04-11

### Added

- **Live lamp preview panel in the menu** - When the terminal is at least 72 columns wide, a second bordered box appears next to the menu rendering a real miniature of the currently-selected configuration. Every selection change is reflected in real time — style, flow, theme, and even koi pond mode (complete with lily pads and fish) render live. Previously only theme cycling gave visual feedback
- **Inline theme palette swatch** - The THEME field now shows 5 colored blocks in the theme's lava palette next to the theme name, so you can compare palettes at a glance without committing
- **Option position indicator** - Every field now shows `(current/total)` next to its value (e.g. `◂ Classic ▸ (1/10)`) so you know how many options exist in each list
- **`R` key in the menu** - Randomizes all five fields at once. Great for "surprise me" discovery across 10 styles × 11 themes × 6 flows
- **`1`–`5` number-key jumps** - Press a digit to jump directly to STYLE, THEME, FLOW, COUNT, or SIZE without j/k-ing through the list
- **Wrap-around menu navigation** - `UP` from STYLE now wraps to the Launch button, and `DOWN` from Launch wraps back to STYLE. No more dead-ends
- **CLI flags for direct launch** - `lavacli --style koipond --theme koi_pond --flow swirl --count 3 --size G` skips the menu entirely and drops straight into the animation. All five fields are optional; omitted ones get sensible defaults. Huge for tmux startup scripts, shell aliases, and screensaver integration
- **`--random` flag** - Randomizes any unspecified fields before launch. Combines with explicit flags (e.g. `--random --style koipond` locks koi pond but randomizes the rest)
- **`--duration SECONDS` flag** - Run for N seconds then exit cleanly. Built for terminal screensaver use (`lavacli --random --duration 600` etc.)
- **`--version` flag** - Prints the installed version
- **`__version__` on the package** - `lavacli.__version__` now exposes the version string in code

### Changed

- **Menu help line rewritten** to reflect the new keys: `↑↓←→ Nav  1-5 Jump  R Rand  Enter  Q Quit`
- **`Pond.render()` now accepts optional `x_off` / `y_off` offsets** so the pond preview can render into an inset region of the menu screen. Default behavior (no offsets) is unchanged
- **`app.run()` now accepts an optional `argv` argument** for argparse testing and programmatic invocation; existing `run()` with no args still works as a setuptools `console_scripts` entry point

### Fixed

- **ColorHelper pond pairs not allocated in the menu** - The koi pond preview panel crashed on first draw because `ColorHelper.setup()` doesn't allocate fish/water color pairs (those normally come from `setup_pond_colors()` inside `_run_pond`). The menu now calls `setup_pond_colors()` during init and refreshes it after every theme change, so the preview can render koi pond without `AttributeError: '_water_pair'`

## [1.2.1] - 2026-04-09

### Fixed

- **README on PyPI** - The 1.2.0 wheel was built before the install section was updated for the `pylavalamp` distribution name, so the live PyPI page contradicted itself ("LavaCLI isn't published to PyPI — install it from a local clone" while being read on the PyPI page). 1.2.1 republishes the package with the correct README: `pipx install pylavalamp`, the real GitHub repo URL, and accurate Python version requirement (3.8+, matching `requires-python`)
- **Stale Python version in README requirements** - was `Python 3.6+`, now matches `pyproject.toml`'s `requires-python = ">=3.8"`
- **Duplicate "Koi Pond Mode" feature bullet** in README — was listed twice, now consolidated into one richer line

### Added

- **PyPI / Python version / License badges** at the top of the README, reading live data from `https://pypi.org/project/pylavalamp/`
- **"Koi Pond" subsection in README "How It Works"** explaining 14-segment fish physics and lily pad rasterization
- **"Solid Base/Cap" README section** now mentions the rocket's serrated three-fin profile and chrome highlight stripe (was still describing the old torpedo rocket)

## [1.2.0] - 2026-04-09

### Added

- **Lily pads in Koi Pond mode** - 6-10 sage-green elliptical lily pads are scattered across the pond at random non-overlapping positions, each with a characteristic V-notch and 3-tone shading (rim/fill/shadow) for a watercolor look. Fish swim *over* the pads
- **Koi Pond theme** - New 11th color theme with teal water, white-orange koi-friendly lava palette, and sage lily pads — matches the watercolor reference aesthetic
- **Lily pad palette in every theme** - All themes now include `lily_pad` / `lily_pad_dark` / `lily_pad_rim` slots so pads stay sage-green regardless of which theme is active
- **`LilyPad` class in `pond.py`** with Poisson-ish placement that scales count and size to pond dimensions, regenerated automatically on terminal resize

### Changed

- **Rocket lamp redesign** - Cylindrical glass column (was torpedo/bullet bulge), sharper and longer pointed nose cone, three distinct swept-back fins suggested by serrated profile valleys, and chrome highlight stripe down the center of the cap and fin base for a polished metal look. Glass column is now framed by chrome columns instead of dark glass border (rocket only). Inspired by the Mathmos rocket reference image
- **Kohaku/Sanke fish bias** - Pond fish init weights kohaku (white with orange) and sanke higher so the default pond reads as a classic koi pond at a glance

### Fixed

- `Pond._fill_width` and `_fill_fin` now correctly overwrite lily pad cells (previously would have raised IndexError when a fish swam over a pad)

## [1.1.0] - 2026-04-07

### Added

- **Koi Pond mode** - New fullscreen style with animated, colorized koi fish swimming around the terminal
- **6 koi color varieties** - Kohaku (orange/white), Sanke (red/white/black), Showa (red/white on black), Tancho (red crown/white), Ogon (solid gold), Asagi (blue-gray/orange)
- **Skeletal fish physics** - 14-segment body chain with constraint-based movement and sinusoidal swimming undulation, inspired by [cpond](https://github.com/ayuzur/cpond)
- **Fish body shape** - Pointed snout, bulging belly, pectoral fins, narrow caudal peduncle, and fanning tail fin
- **Pond color system** - Fish-on-water color pair allocation with per-body-part coloring (head, body patches, fins, tail)
- New `pond.py` module with `Segment`, `Fish`, and `Pond` classes
- `B`/`V` keys add/remove fish in Koi Pond mode
- All 10 themes work with Koi Pond (water color adapts to theme liquid)

## [1.0.0] - 2026-04-07

### Added

- **Global install via pipx** - `pipx install lavacli` makes the `lavacli` command available from anywhere in the terminal
- **`pyproject.toml`** - Standard Python packaging with `console_scripts` entry point

## [0.3.0] - 2026-04-07

### Added

- **Rocket style** - Mathmos Telstar-inspired rocket ship lava lamp with pointed nose cone and swept-back fin base
- **Cylinder style** - Vintage straight-tube lava lamp with flat disc cap and simple cone base
- **Pear style** - Retro bulbous shape with narrow neck and wide belly
- **Freestyle mode** - Fullscreen lava fills the entire terminal with no lamp frame
- **Liquid flow type** - Pure-Python 3D Perlin noise with fractal Brownian motion for smooth organic flowing patterns
- **Rim/edge glow effect** - Dual-threshold metaball rendering creates a glowing halo around each lava blob
- **Groovy animated menu** - Lava background animation, rotating groovy taglines, decorative border, live theme preview
- **3 new themes** - Blue Purple, Clear Red, Clear Orange (inspired by classic Lava Library color codes)
- **Return to menu** - Press `M` during animation to go back to the menu
- **Toggle HUD** - Press `H` to show/hide the bottom controls bar for a clean view
- Pure-Python `noise.py` module with Perlin noise and FBM (no external dependencies)

### Changed

- **10 color themes** (was 7) - all renamed to clean names, inspired by 1992-2004 Lava Library catalog
- **Dark bases** - All themes now use dark gray/black bases matching classic lava lamp aesthetics
- **Dark glass frame outline** - Glass border uses dark contrasting color for pixel-art style definition
- **Improved base profile** - Proper hourglass shape matching the real Lava Original silver base
- **Improved cap profile** - Wide cylindrical collar band instead of tiny dome
- **3-tone metallic shading** - Base and cap use highlight/mid/shadow for richer metallic appearance
- **Fixed cap rendering bug** - Cap was invisible due to coordinate system mismatch (absolute vs local)
- **Wider glass top** - Classic shape now starts at 0.36 width (was 0.22) matching real lamp proportions
- **Better proportions** - Glass ~57%, Base ~34%, Cap ~8% of total height (was ~73%/22%/5%)
- **More blobs** - Default ball counts increased for more impressive display
- **Faster animation** - ~20fps (was ~14fps) for smoother lava flow
- **9 styles** (was 5) - added Cylinder, Pear, Rocket, and Freestyle
- **6 flow types** (was 5) - added Liquid (Perlin noise)
- Menu now shows only selected option per field (no overflow)

## [0.2.0] - 2026-04-06

### Changed

- Completely redesigned lamp shapes to match real lava lamp silhouettes (conical: narrow top, wide bottom)
- Replaced outline-only base/cap with solid filled metallic rendering using half-blocks
- Added colored liquid backgrounds per theme (purple, navy, forest green, etc.) instead of plain dark gray
- Added hourglass-shaped base profile with highlight/shadow shading
- Expanded sizes to 5 options matching real dimensions: 11.5", 14.5", 16.3", 17", 27" Grande
- Default size is now 27" Grande
- Default lamp count is now 1
- Improved metaball blob shape (slightly more organic vertical proportion)
- Tighter body padding for cleaner look

## [0.1.0] - 2026-04-06

### Added

- Initial release
- Interactive curses-based menu for configuring lamps
- 5 lamp styles: Classic, Slim, Globe, Lava, Diamond
- 7 color themes with 256-color support
- 5 flow types including swirl vortex physics
- 1-6 simultaneous lamps with terminal resize support
- Half-block Unicode rendering for 2x vertical resolution
- Metaball physics engine with heat/buoyancy cycle
- Runtime controls: speed, pause, color cycling, blob add/remove, reset
- Zero external dependencies (Python stdlib only)
