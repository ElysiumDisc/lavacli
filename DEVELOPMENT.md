# Development Guide

## Prerequisites

- Python 3.6+
- A terminal emulator with Unicode and 256-color support
- Linux or macOS (curses is built-in); Windows requires `windows-curses` package

## Project Structure

```
lavacli/
├── run.py                  # Convenience runner
├── lavacli/
│   ├── __init__.py         # Package marker
│   ├── __main__.py         # Entry point (python -m lavacli)
│   ├── app.py              # Main curses app loop, layout, input handling
│   ├── lamp.py             # Lamp class: shapes, metaball physics, rendering
│   ├── menu.py             # Interactive selection menu
│   └── themes.py           # Color themes and ColorHelper class
├── README.md
├── CHANGELOG.md
└── DEVELOPMENT.md
```

## Running

```bash
# Using the module
python3 -m lavacli

# Using the convenience script
python3 run.py
```

## Architecture

### Key Modules

| File | Purpose |
|------|---------|
| `app.py` | Curses setup, animation loop, input dispatch, layout, resize handling |
| `lamp.py` | Core simulation: shape profiles, `Ball`/`Lamp` classes, metaball field computation, half-block rendering, solid base/cap rendering |
| `themes.py` | Theme definitions (7 themes with colored liquids), `ColorHelper` for curses color pair management |
| `menu.py` | Interactive TUI menu |

### Rendering Pipeline

Each frame:

1. **Input** - `screen.getch()` with timeout (acts as frame limiter at ~14fps)
2. **Physics** - `Lamp.update()` advances ball positions, temperature, collisions
3. **Render** - `screen.erase()`, then for each lamp:
   - **Cap** - Solid metallic dome rendered with half-blocks
   - **Body** - Compute metaball field at each half-cell, map to lava intensity, draw with colored liquid background
   - **Base** - Solid metallic hourglass rendered with half-blocks and highlight/shadow
4. **Refresh** - `noutrefresh()` + `doupdate()` for flicker-free output

### Shape System

Shapes are defined as normalized profiles: `[(y, width), ...]` where `y` ranges 0-1 (top to bottom) and `width` ranges 0-1 (fraction of max width). All shapes are **conical** (narrow at top, wide at bottom) to match real lava lamp silhouettes. Interpolation uses smoothstep (cubic Hermite) for smooth curves.

The base uses a separate `BASE_PROFILE` defining the hourglass/pedestal shape, and the cap uses `CAP_PROFILE` for the small dome.

### Size System

Five sizes modeled after real lava lamp dimensions:

| Key | Name | Body (HxW) | Base H | Cap H | Balls | Radius |
|-----|------|-----------|--------|-------|-------|--------|
| S | 11.5" | 14x8 | 5 | 2 | 3 | 1.8 |
| M | 14.5" | 20x12 | 6 | 2 | 4 | 2.4 |
| L | 16.3" | 26x14 | 8 | 3 | 5 | 3.0 |
| XL | 17" | 30x16 | 9 | 3 | 6 | 3.4 |
| G | 27" Grande | 40x22 | 12 | 3 | 8 | 4.5 |

Sizes auto-scale to fit the terminal. The default is 27" Grande.

### Color Pair Management

`ColorHelper` pre-allocates curses color pairs for all needed foreground/background combinations:

- `(N+1)^2` pairs for lava/liquid combos (N = 5 lava levels + liquid background)
- Additional pairs for base highlight/shadow, borders, text, UI elements

Each theme defines a `liquid` color (the colored background visible inside the glass) in addition to the lava gradient colors, creating the authentic colored-liquid look of real lava lamps.

### Physics Parameters

Each flow type is a dict of physics parameters:

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

## Adding a New Theme

In `themes.py`, add to the `THEMES` dict:

```python
'my_theme': {
    'name': 'My Theme',
    'lava': [c1, c2, c3, c4, c5],  # 5 ANSI 256-color codes, dim to bright
    'liquid': 53,                    # colored liquid background
    'base_color': 249,               # metallic base highlight
    'base_shadow': 243,              # metallic base shadow
    'border': 96,                    # subtle glass edge color
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

Then add `'my_shape'` to `SHAPE_ORDER`.

## Adding a New Flow Type

In `lamp.py`, add to the `FLOW_PARAMS` dict:

```python
'my_flow': {
    'gravity': 0.010, 'buoyancy': 0.020, 'damping': 0.98,
    'random_force': 0.005, 'swirl': 0.0, 'bounce': 0.6,
    'heat_rate': 0.012, 'cool_rate': 0.008,
},
```

Then add `'my_flow'` to `FLOW_ORDER`.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Terminal too small` | Resize terminal to at least 46x20 |
| No colors / garbled output | Ensure `TERM` is set to `xterm-256color` or similar |
| Unicode boxes instead of smooth blobs | Terminal needs Unicode support; try a modern emulator |
| Flickering | Try reducing lamp count or using a GPU-accelerated terminal |
| Import error on Windows | Install `windows-curses`: `pip install windows-curses` |
