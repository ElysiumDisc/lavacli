# Changelog

All notable changes to LavaCLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
