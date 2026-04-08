# LavaCLI

A beautiful, interactive terminal lava lamp simulator with metaball physics, Perlin noise flow, half-block rendering, and full customization.

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

- **10 Lamp Styles** - Classic, Slim, Globe, Lava, Diamond, Cylinder, Pear, Rocket (Mathmos Telstar), Freestyle (fullscreen lava), and Koi Pond (fullscreen animated fish)
- **10 Color Themes** - Yellow Red, Blue White, Clear Orange, Purple Haze, Neon Green, Blue Purple, Clear Red, Sunset, Psychedelic, Monochrome - inspired by classic 1992-2004 Lava Library color codes
- **6 Flow Types** - Classic, Chaotic, Zen, Bouncy, Swirl, and Liquid (Perlin noise organic flow)
- **Koi Pond Mode** - Fullscreen animated koi pond with colorized fish (6 real koi varieties: Kohaku, Sanke, Showa, Tancho, Ogon, Asagi) using skeletal segment-based physics
- **1-6 Lamps** - Display multiple lava lamps side by side
- **5 Sizes** - 11.5", 14.5", 16.3", 17", and 27" Grande (default)
- **Freestyle Mode** - Fullscreen lava with no lamp frame, filling the entire terminal
- **Koi Pond Mode** - Fullscreen swimming koi fish with beautiful coloring, pectoral fins, and fanning tail fins
- **Groovy Animated Menu** - Lava background, rotating taglines, live theme preview
- **Rim/Edge Glow** - Dual-threshold rendering gives lava blobs a glowing halo edge
- **Resizable** - Lamps adapt when you resize the terminal
- **Half-Block Rendering** - Uses Unicode `▀▄█` characters for 2x vertical resolution
- **Metaball Physics** - Real metaball field simulation for authentic blob merging/splitting
- **Perlin Noise Flow** - Pure-Python 3D Perlin noise with fractal Brownian motion for smooth organic liquid animation
- **Heat/Buoyancy Cycle** - Blobs heat at the bottom, rise, cool at the top, and sink back down
- **Dark Metallic Base** - Hourglass-shaped base with 3-tone shading, matching classic black lava lamp bases
- **Rocket Style** - Mathmos Telstar-inspired rocket ship with pointed nose cone and swept-back fins
- **Interactive Controls** - Change speed, pause, cycle colors, add/remove blobs, return to menu, toggle HUD

## Install

```bash
pipx install lavacli
```

That's it — `lavacli` is now available as a command from anywhere in your terminal.

To install from a local clone instead:

```bash
pipx install /path/to/lavacli
```

For development (editable mode, changes take effect immediately):

```bash
pipx install -e /path/to/lavacli
```

### Uninstall

```bash
pipx uninstall lavacli
```

## Quick Start

```bash
lavacli
```

Or run directly without installing:

```bash
python3 -m lavacli
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
| `M` | Return to menu |
| `Space` | Pause / Resume |
| `+` / `=` | Speed up (up to 300%) |
| `-` | Slow down (down to 25%) |
| `C` | Cycle color theme |
| `B` | Add a blob (or fish in Koi Pond mode) |
| `V` | Remove a blob (or fish in Koi Pond mode) |
| `R` | Reset all lamps |
| `H` | Toggle HUD (show/hide bottom bar) |

## Styles

| Style | Description |
|-------|-------------|
| Classic | The iconic 16.3" conical lava lamp |
| Slim | Straighter taper, 14.5" profile |
| Globe | Rounded bulbous shape, wider in upper portion |
| Lava | Organic wavy silhouette |
| Diamond | Angular, widest at center |
| Cylinder | Straight tube with flat cap and cone base (vintage style) |
| Pear | Retro bulbous shape with narrow neck and wide belly |
| Rocket | Mathmos Telstar rocket ship with pointed nose and swept fins |
| Freestyle | No lamp frame - fullscreen lava fills the terminal |
| Koi Pond | Fullscreen animated koi pond with colorized swimming fish |

## Themes

Inspired by the classic 1992-2004 Lava Library color codes with dark bases:

| Theme | Lava | Liquid |
|-------|------|--------|
| Yellow Red | Red-orange-yellow gradient | Yellow |
| Blue White | White-to-blue gradient | Blue |
| Clear Orange | Orange-gold gradient | Clear/dark |
| Purple Haze | Pink-magenta gradient | Dark purple |
| Neon Green | Bright green-cyan | Forest green |
| Blue Purple | Purple-lavender gradient | Deep blue |
| Clear Red | Bright red-rose | Clear/dark |
| Sunset | Red-orange-yellow | Maroon |
| Psychedelic | Rainbow | Navy |
| Monochrome | Gray-to-white | Black |

## Flow Types

| Flow | Description |
|------|-------------|
| Classic | Standard gravity + buoyancy cycle |
| Chaotic | Stronger forces, more unpredictable |
| Zen | Slow, peaceful drift |
| Bouncy | High elasticity, balls bounce energetically |
| Swirl | Vortex physics spiraling around the center |
| Liquid | Perlin noise organic flow - smooth, flowing patterns instead of distinct blobs |

## Koi Pond

Select **Koi Pond** from the STYLE menu for a fullscreen animated koi pond. Fish are rendered with the same half-block technique as the lava lamp, but use skeletal segment-based physics inspired by [cpond](https://github.com/ayuzur/cpond).

Each fish has 14 connected body segments with constraint-based movement, sinusoidal swimming undulation, pectoral fins, and a fanning tail fin. Fish are colorized using 6 real koi varieties:

| Variety | Colors |
|---------|--------|
| Kohaku | Orange-red markings on white body |
| Sanke | Red patches on white with black accents |
| Showa | Red and white on black body |
| Tancho | Red crown on clean white body |
| Ogon | Solid metallic gold |
| Asagi | Blue-gray back with orange belly |

Fish colors adapt to the selected theme's liquid color as the water background. Use `B`/`V` to add/remove fish, and `C` to cycle themes.

## Sizes

Modeled after real lava lamp dimensions:

| Size | Name | Description |
|------|------|-------------|
| S | 11.5" | Compact desk lamp |
| M | 14.5" | Standard size |
| L | 16.3" | Classic 52oz |
| XL | 17" | Large |
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

When the field exceeds a threshold, that pixel is "inside" the lava. Nearby blobs naturally merge into smooth shapes. A secondary rim threshold creates a glowing edge around each blob for visual depth.

### Perlin Noise Flow

The "Liquid" flow type uses 3D Perlin noise with fractal Brownian motion (3 octaves) instead of metaball physics. Time advances continuously through the noise field, creating smooth organic flowing patterns. No ball physics needed - just `fbm3(x * scale, y * scale, time)`.

### Heat/Buoyancy Cycle

Balls track a temperature value. Near the bottom they heat up and gain buoyancy. As they rise to the top they cool down and gravity pulls them back. This creates the mesmerizing rise-and-fall cycle of a real lava lamp.

### Half-Block Rendering

Each terminal cell is split into two vertical halves using Unicode half-block characters (`▀▄█`), doubling the effective vertical resolution for smooth blob edges.

### Solid Base/Cap

The metallic base and cap are rendered as filled shapes using half-block characters with 3-tone highlight/mid/shadow shading. The base uses a classic hourglass profile. The rocket style uses pointed nose cone and swept-back fin profiles.

## License

MIT
