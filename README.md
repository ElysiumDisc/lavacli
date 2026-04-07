# LavaCLI

A beautiful, interactive terminal lava lamp simulator with metaball physics, half-block rendering, and full customization.

```
      ╭─╮              ╭─╮              ╭─╮
   ╭──┘ └──╮        ╭──┘ └──╮        ╭──┘ └──╮
   │        │        │        │        │        │
   │  ▄██▄  │        │        │        │   ▄▄   │
  ╱  ██████  ╲      ╱   ▄▄▄   ╲      ╱   ████   ╲
  │  ▀████▀  │      │  █████  │      │  ██████  │
  │   ▀▀▀▀   │      │  █████  │      │  ▀████▀  │
  │           │      │  ▀███▀  │      │   ▀▀▀▀   │
  │    ▄▄▄   │      │   ▀▀    │      │           │
  │   █████  │      │         │      │   ▄▄▄▄   │
  │   █████  │      │  ▄▄     │      │  ██████  │
  │   ▀███▀  │      │  ██▄    │      │  ██████  │
   ╲   ▀▀   ╱        ╲  ▀▀   ╱        ╲  ▀██▀   ╱
   │        │        │        │        │        │
   ╰──┐ ┌──╯        ╰──┐ ┌──╯        ╰──┐ ┌──╯
      ╰─╯              ╰─╯              ╰─╯
   ═══════════════════════════════════════════
```

## Features

- **5 Lamp Styles** - Classic, Slim, Globe, Lava, Diamond - each with a unique curved profile
- **7 Color Themes** - Retro Red, Ocean Blue, Neon Green, Sunset, Purple Haze, Psychedelic, Monochrome
- **5 Flow Types** - Classic, Chaotic, Zen, Bouncy, Swirl (with vortex physics!)
- **1-6 Lamps** - Display multiple lava lamps side by side
- **3 Sizes** - Small, Medium, Large
- **Resizable** - Lamps adapt when you resize the terminal
- **Half-Block Rendering** - Uses Unicode `▀▄█` characters for 2x vertical resolution, creating smooth blob shapes
- **Metaball Physics** - Real metaball field simulation for authentic blob merging/splitting
- **Heat/Buoyancy Cycle** - Blobs heat at the bottom, rise, cool at the top, and sink back down
- **Interactive Controls** - Change speed, pause, cycle colors, add/remove blobs in real time
- **Decorative Elements** - Caps, bases, curved borders, and a shelf

## Quick Start

```bash
python3 -m lavacli
```

Or use the convenience script:

```bash
python3 run.py
```

## Controls

### Menu

| Key | Action |
|-----|--------|
| `Up/Down` or `j/k` | Navigate between options |
| `Left/Right` or `h/l` | Change selection |
| `Enter` | Launch the lava lamp |
| `Q` / `Esc` | Quit |

### During Animation

| Key | Action |
|-----|--------|
| `Q` / `Esc` | Quit |
| `Space` | Pause / Resume |
| `+` / `=` | Speed up (up to 300%) |
| `-` | Slow down (down to 25%) |
| `C` | Cycle color theme |
| `B` | Add a blob to each lamp |
| `V` | Remove a blob from each lamp |
| `R` | Reset all lamps |

## Requirements

- Python 3.6+
- A terminal with:
  - Unicode support (for half-block characters `▀▄█` and box-drawing)
  - 256-color support (for full color themes; falls back to 8 colors)
  - Minimum 50x22 characters (larger recommended for multiple lamps)

No external dependencies - uses only Python standard library (`curses`).

## How It Works

### Metaball Physics

Each lava blob is a "metaball" - a point with a radius that generates an implicit field. For each pixel on screen, the field contributions from all balls are summed:

```
field(x,y) = sum( radius^2 / distance^2 ) for each ball
```

When the field exceeds a threshold, that pixel is "inside" the lava. Because the field is additive, nearby blobs naturally merge into smooth shapes - the hallmark lava lamp effect.

### Heat/Buoyancy Cycle

Balls track a temperature value. Near the bottom of the lamp, they heat up and gain buoyancy (upward force exceeding gravity). As they rise and reach the top, they cool down, lose buoyancy, and gravity pulls them back. This creates the mesmerizing rise-and-fall cycle of a real lava lamp.

### Half-Block Rendering

Each terminal cell is split into two vertical halves using Unicode half-block characters:
- `▀` (upper half) - top half is foreground color, bottom is background
- `▄` (lower half) - bottom half is foreground, top is background
- `█` (full block) - entire cell is one color

This doubles the effective vertical resolution, making blob edges significantly smoother.

## License

MIT
