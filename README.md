# LavaCLI

A beautiful, interactive terminal lava lamp simulator with metaball physics, half-block rendering, and full customization.

```
          ╭─╮
        ╭─┘ └─╮
        │      │
        │ ▄██▄ │
       ╱ █████  ╲
      │  ▀████▀  │
      │   ▀▀▀▀   │
      │           │
     ╱    ▄▄▄     ╲
     │   █████     │
    ╱   ██████▄     ╲
    │   ████████    │
    │   ▀██████▀    │
   ╱     ▀▀▀▀▀      ╲
   │                  │
   │      ▄▄▄▄▄      │
  ╱      ███████      ╲
  │     █████████      │
  │     █████████      │
  │      ▀█████▀       │
  ████████████████████
   ████████████████
     ████████████
       ████████
     ████████████
   ████████████████
  ████████████████████
  ══════════════════════
```

## Features

- **5 Lamp Styles** - Classic, Slim, Globe, Lava, Diamond - conical profiles matching real lava lamp silhouettes
- **7 Color Themes** - Retro Red, Ocean Blue, Neon Green, Sunset, Purple Haze, Psychedelic, Monochrome - each with colored liquid backgrounds just like real lamps
- **5 Flow Types** - Classic, Chaotic, Zen, Bouncy, Swirl (with vortex physics)
- **1-6 Lamps** - Display multiple lava lamps side by side
- **5 Sizes** - 11.5", 14.5", 16.3", 17", and 27" Grande (default)
- **Resizable** - Lamps adapt when you resize the terminal
- **Half-Block Rendering** - Uses Unicode `▀▄█` characters for 2x vertical resolution
- **Metaball Physics** - Real metaball field simulation for authentic blob merging/splitting
- **Heat/Buoyancy Cycle** - Blobs heat at the bottom, rise, cool at the top, and sink back down
- **Solid Metallic Base** - Hourglass-shaped base rendered with filled half-blocks
- **Interactive Controls** - Change speed, pause, cycle colors, add/remove blobs in real time
- **Colored Liquid** - Each theme has a distinct liquid color (purple, navy, forest green, etc.)

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

## Sizes

Modeled after real lava lamp dimensions:

| Size | Name | Description |
|------|------|-------------|
| S | 11.5" | Compact desk lamp |
| M | 14.5" | Standard size |
| L | 16.3" | Classic 52oz |
| XL | 17" | Large 32oz |
| **G** | **27" Grande** | **The showpiece (default)** |

## Requirements

- Python 3.6+
- A terminal with:
  - Unicode support (for half-block characters `▀▄█`)
  - 256-color support (for full color themes; falls back to 8 colors)
  - Minimum 46x20 characters (larger recommended for Grande size)

No external dependencies - uses only Python standard library (`curses`).

## How It Works

### Metaball Physics

Each lava blob is a "metaball" - a point with a radius that generates an implicit field:

```
field(x,y) = sum( radius^2 / distance^2 ) for each ball
```

When the field exceeds a threshold, that pixel is "inside" the lava. Nearby blobs naturally merge into smooth shapes.

### Heat/Buoyancy Cycle

Balls track a temperature value. Near the bottom they heat up and gain buoyancy. As they rise to the top they cool down and gravity pulls them back. This creates the mesmerizing rise-and-fall cycle of a real lava lamp.

### Half-Block Rendering

Each terminal cell is split into two vertical halves using Unicode half-block characters (`▀▄█`), doubling the effective vertical resolution for smooth blob edges.

### Solid Base/Cap

The metallic base and cap are rendered as filled shapes using half-block characters with highlight/shadow colors, creating the iconic hourglass pedestal.

## License

MIT
