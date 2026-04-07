# Changelog

All notable changes to LavaCLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
