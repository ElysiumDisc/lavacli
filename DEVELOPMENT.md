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

### From the project root

```bash
# Using the module
python3 -m lavacli

# Using the convenience script
python3 run.py
```

### Key modules

| File | Purpose |
|------|---------|
| `app.py` | Curses setup, animation loop, input dispatch, layout calculation, resize handling |
| `lamp.py` | Core simulation: shape profiles, `Ball`/`Lamp` classes, metaball field computation, half-block rendering |
| `themes.py` | Theme definitions (7 themes), `ColorHelper` for curses color pair management |
| `menu.py` | Interactive TUI menu using curses |

## Architecture

### Rendering Pipeline

Each frame:

1. **Input** - `screen.getch()` with timeout (acts as frame limiter)
2. **Physics** - `Lamp.update()` advances ball positions, temperature, collisions
3. **Render** - `screen.erase()`, then for each lamp:
   - Compute screen bounds from shape profile
   - For each cell: compute metaball field at top/bottom half-rows
   - Map field strength to lava intensity level (0-5)
   - Draw half-block character with appropriate color pair
   - Draw side borders with diagonal chars for curves
   - Draw cap (with top horizontal border) and base
4. **Refresh** - `noutrefresh()` + `doupdate()` for flicker-free output

### Shape System

Shapes are defined as normalized profiles: `[(y, width), ...]` where `y` ranges 0-1 (top to bottom) and `width` ranges 0-1 (fraction of max width). The `Lamp` class interpolates these using smoothstep (cubic Hermite) for smooth curves, then quantizes to integer column positions for rendering.

### Color Pair Management

`ColorHelper` pre-allocates curses color pairs for all needed foreground/background combinations:

- `(N+1)^2` pairs for lava level x lava level combos (N = 5 lava levels + glass)
- Additional pairs for borders, base, text, UI elements

Half-block rendering requires precise fg/bg pairing since `▀` uses fg for the top half and bg for the bottom half.

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
    'glass': 234,                    # interior background color
    'border': 245,                   # lamp outline color
    'base': 240,                     # cap/base color
    'glow': 52,                      # ambient glow color
},
```

Then add `'my_theme'` to `THEME_ORDER`.

## Adding a New Shape

In `lamp.py`, add to the `SHAPES` dict:

```python
'my_shape': [
    (0.00, 0.30),  # (normalized_y, normalized_width)
    (0.25, 0.80),  # width should be > 0.15 at extremes
    (0.50, 1.00),  # 1.0 = full lamp width
    (0.75, 0.80),
    (1.00, 0.30),
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
| `Terminal too small` | Resize terminal to at least 50x22 |
| No colors / garbled output | Ensure `TERM` is set to `xterm-256color` or similar |
| Unicode boxes instead of smooth curves | Terminal needs Unicode support; try a modern emulator |
| Flickering | Terminal may not support double-buffering well; try reducing lamp count |
| Import error on Windows | Install `windows-curses`: `pip install windows-curses` |
