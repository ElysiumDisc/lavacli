# Development Guide

## Prerequisites

- Python 3.6+
- A terminal emulator with Unicode and 256-color support
- Linux or macOS (curses is built-in); Windows requires `windows-curses` package

## Project Structure

```
lavacli/
├── pyproject.toml              # Packaging config (version, entry point)
├── run.py                      # Convenience runner
├── lavacli/
│   ├── __init__.py             # Package marker
│   ├── __main__.py             # Entry point (python -m lavacli)
│   ├── app.py                  # Main curses app loop, layout, input handling
│   ├── lamp.py                 # Lamp class: shapes, metaball physics, rendering
│   ├── menu.py                 # Interactive animated selection menu
│   ├── noise.py                # Pure-Python 3D Perlin noise + FBM
│   └── themes.py               # Color themes and ColorHelper class
├── README.md
├── CHANGELOG.md
└── DEVELOPMENT.md
```

## Install

```bash
# Install globally (available from anywhere)
pipx install /path/to/lavacli

# Editable install (source changes take effect immediately)
pipx install -e /path/to/lavacli

# Uninstall
pipx uninstall lavacli
```

## Running

```bash
# After install
lavacli

# Without installing — from the project directory
python3 -m lavacli

# Using the convenience script
python3 run.py
```

## Architecture

### Key Modules

| File | Purpose |
|------|---------|
| `app.py` | Curses setup, animation loop (~20fps), input dispatch, layout, resize handling, menu-to-lamp flow |
| `lamp.py` | Core simulation: shape profiles (including rocket), `Ball`/`Lamp` classes, metaball field computation, Perlin noise field, half-block rendering, solid base/cap/frame rendering |
| `noise.py` | Pure-Python 3D Perlin noise implementation with fractal Brownian motion (FBM) for the Liquid flow type |
| `themes.py` | 10 theme definitions (classic Lava Library colors, dark bases), `ColorHelper` for curses color pair management, frame/base/cell drawing methods |
| `menu.py` | Animated TUI menu with lava background, groovy taglines, live theme preview |

### Rendering Pipeline

Each frame (~20fps):

1. **Input** - `screen.getch()` with 50ms timeout (acts as frame limiter)
2. **Physics** - `Lamp.update()` advances ball positions/temperature/collisions (metaball flows) or noise time (liquid flow)
3. **Render** - `screen.erase()`, then for each lamp:
   - **Cap** - Solid metallic collar/nose cone with 3-tone shading and half-blocks
   - **Body** - Dark frame outline + compute field at each half-cell, map to lava intensity (with rim glow), draw with colored liquid background
   - **Base** - Solid metallic hourglass/fins with 3-tone highlight/mid/shadow
4. **HUD** - Controls bar at bottom (toggleable with `H`)
5. **Refresh** - `noutrefresh()` + `doupdate()` for flicker-free output

### Shape System

Shapes are defined as normalized profiles: `[(y, width), ...]` where `y` ranges 0-1 (top to bottom) and `width` ranges 0-1 (fraction of max width). Interpolation uses smoothstep (cubic Hermite) for smooth curves.

9 styles available:

| Style | Shape | Profile |
|-------|-------|---------|
| Classic | Conical (narrow top, wide bottom) | `SHAPES['classic']` |
| Slim | Straighter taper | `SHAPES['slim']` |
| Globe | Bulbous, wider at top | `SHAPES['globe']` |
| Lava | Organic wavy | `SHAPES['lava']` |
| Diamond | Angular, widest at center | `SHAPES['diamond']` |
| Cylinder | Straight tube, flat sides | `SHAPES['cylinder']` + `CYLINDER_CAP_PROFILE` + `CYLINDER_BASE_PROFILE` |
| Pear | Bulbous belly, narrow neck | `SHAPES['pear']` |
| Rocket | Torpedo/bullet, widest in middle | `SHAPES['rocket']` + `ROCKET_CAP_PROFILE` + `ROCKET_BASE_PROFILE` |
| Freestyle | Full-width rectangle | `SHAPES['freestyle']` (no frame) |

Style-specific profiles are selected via `Lamp._get_cap_profile()` and `Lamp._get_base_profile()`. The default base uses `BASE_PROFILE` (hourglass pedestal), rocket uses `ROCKET_BASE_PROFILE` (swept fins), and cylinder uses `CYLINDER_BASE_PROFILE` (simple cone).

### Size System

Five sizes modeled after real lava lamp dimensions (proportions: glass ~57%, base ~34%, cap ~8%):

| Key | Name | Body (HxW) | Base H | Cap H | Balls | Radius |
|-----|------|-----------|--------|-------|-------|--------|
| S | 11.5" | 12x8 | 7 | 2 | 4 | 1.8 |
| M | 14.5" | 16x12 | 10 | 2 | 6 | 2.4 |
| L | 16.3" | 20x14 | 12 | 3 | 7 | 3.0 |
| XL | 17" | 24x16 | 14 | 3 | 8 | 3.4 |
| G | 27" Grande | 30x22 | 18 | 4 | 10 | 4.5 |

Sizes auto-scale to fit the terminal. Rocket style gets a taller nose cone and fin base.

### Color Pair Management

`ColorHelper` pre-allocates curses color pairs for all needed foreground/background combinations:

- `N^2` pairs for all lava/liquid/rim combos (7 renderable colors: liquid + 5 lava + rim)
- 9 metallic pairs for 3-tone base shading (highlight/mid/shadow combinations)
- 3 border pairs for glass frame outline
- Additional pairs for text, UI, accent elements

Each theme defines: `lava` (5 intensity colors), `liquid` (background), `rim` (glow edge), `base_color`/`base_mid`/`base_shadow` (3-tone metallic), and `border` (dark glass outline).

### Physics Parameters

Each metaball flow type is a dict of physics parameters:

| Parameter | Effect |
|-----------|--------|
| `gravity` | Downward force on all balls |
| `buoyancy` | Upward force scaled by ball temperature |
| `damping` | Velocity multiplier per frame (< 1.0 = drag) |
| `random_force` | Gaussian noise for organic movement |
| `swirl` | Circular force strength around lamp center |
| `bounce` | Elasticity of wall collisions (0-1) |
| `heat_rate` | How fast balls heat up at the bottom |
| `cool_rate` | How fast balls cool at the top |

The **Liquid** flow type bypasses ball physics entirely and uses Perlin noise parameters: `noise_scale` (spatial frequency), `noise_speed` (time increment per frame), and `noise_octaves` (FBM layers).

### Perlin Noise (noise.py)

Pure-Python implementation of classic 3D Perlin noise with:

- Standard permutation table and gradient function
- `noise3(x, y, z)` - single-octave 3D Perlin noise, returns [-1, 1]
- `fbm3(x, y, z, octaves)` - fractal Brownian motion layering multiple octaves for richer detail

Used by `Lamp._compute_noise_field()` which maps noise output to the metaball field range (0-6+) for compatibility with `field_to_level()`.

## Adding a New Theme

In `themes.py`, add to the `THEMES` dict:

```python
'my_theme': {
    'name': 'My Theme',
    'lava': [c1, c2, c3, c4, c5],  # 5 ANSI 256-color codes, dim to bright
    'liquid': 53,                    # colored liquid background
    'rim': 88,                       # glow edge color (between liquid and first lava)
    'base_color': 240,               # metallic base highlight (dark gray for black base)
    'base_mid': 237,                 # metallic mid-tone
    'base_shadow': 234,              # metallic shadow (near black)
    'border': 16,                    # dark glass frame outline
    'glow': 52,                      # ambient glow color
},
```

Then add `'my_theme'` to `THEME_ORDER`.

## Adding a New Shape

In `lamp.py`, add to the `SHAPES` dict:

```python
'my_shape': [
    (0.00, 0.25),   # narrow top
    (0.50, 0.70),   # widens
    (1.00, 1.00),   # widest at bottom (conical)
],
```

Then add `'my_shape'` to `SHAPE_ORDER`. For custom cap/base profiles (like rocket), define separate profile arrays and add conditionals in `_cap_bounds_at()` and `_base_bounds_at()`.

## Adding a New Flow Type

In `lamp.py`, add to the `FLOW_PARAMS` dict:

```python
'my_flow': {
    'gravity': 0.010, 'buoyancy': 0.020, 'damping': 0.98,
    'random_force': 0.005, 'swirl': 0.0, 'bounce': 0.6,
    'heat_rate': 0.012, 'cool_rate': 0.008,
},
```

Then add `'my_flow'` to `FLOW_ORDER`. For non-metaball flows (like Liquid), add special handling in `Lamp.update()` and `Lamp.compute_field()`.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Terminal too small` | Resize terminal to at least 46x20 |
| No colors / garbled output | Ensure `TERM` is set to `xterm-256color` or similar |
| Unicode boxes instead of smooth blobs | Terminal needs Unicode support; try a modern emulator |
| Flickering | Try reducing lamp count or using a GPU-accelerated terminal |
| Import error on Windows | Install `windows-curses`: `pip install windows-curses` |
| Liquid flow too slow | Reduce terminal size or increase `noise_speed` parameter |
