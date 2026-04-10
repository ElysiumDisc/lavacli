# Changelog

All notable changes to LavaCLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
