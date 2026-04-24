# LavaCLI

[![PyPI version](https://img.shields.io/pypi/v/pylavalamp.svg)](https://pypi.org/project/pylavalamp/) [![Python](https://img.shields.io/pypi/pyversions/pylavalamp.svg)](https://pypi.org/project/pylavalamp/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A beautiful, interactive terminal lava lamp simulator with metaball physics, Perlin noise flow, half-block rendering, a fullscreen koi pond, and a theme-cycling spinning ASCII donut. Published on PyPI as **[`pylavalamp`](https://pypi.org/project/pylavalamp/)**.

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

- **14 Lamp Styles** - Classic, Slim, Globe, Lava, Diamond, Cylinder, Pear, Rocket (Mathmos Telstar), Freestyle (fullscreen lava), Koi Pond (fullscreen animated fish), Fireplace (fullscreen embers), Campfire (fullscreen embers + pine forest scene), Donut (fullscreen spinning ASCII donut), and Christmas (fullscreen indoor fireplace with brick surround, mantel, and stockings)
- **17 Color Themes** - Yellow Red, Blue White, Clear Orange, Purple Haze, Neon Green, Blue Purple, Clear Red, Sunset, Psychedelic, Monochrome, Koi Pond, Aurora, Campfire, Cyberpunk, Matrix, Oceanic, and Christmas - inspired by classic 1992-2004 Lava Library color codes and modern neon aesthetics
- **Bi-color Lava** - Mix two themes in a single lamp (like the 90s red/blue Mathmos bi-color lamps) via `--bicolor THEME_B` or the menu's TINT field. Half the blobs carry each palette and merge naturally at their boundaries
- **Motion Trails** - Press `T` during animation to toggle slow-shutter trails; each blob paints a soft fading comet-tail behind it. Works on all lamp and fullscreen styles
- **6 Flow Types** - Classic, Chaotic, Zen, Bouncy, Swirl, and Liquid (Perlin noise organic flow)
- **Koi Pond Mode** - Fullscreen animated koi pond with 6-10 sage-green lily pads scattered across the water and colorized fish (6 real koi varieties: Kohaku, Sanke, Showa, Tancho, Ogon, Asagi) using 14-segment skeletal physics, pectoral fins, and fanning tail fins
- **Campfire Mode** - Dedicated fullscreen campfire with rising ember physics and a layered pine forest silhouette background: three depth layers of conifers, rolling snowy ground with warm firelight glow, and a starry night sky
- **Christmas Fireplace Mode** - Fullscreen indoor Christmas fireplace: red brick surround with lintel, wooden mantel shelf, two Christmas stockings with white cuffs, a procedural dancing hearth flame (black backdrop tapering from white-hot center to dark red edges, with time-based flicker), metaball embers rising on top for depth, stone hearth, and a warm dark room with hardwood floor
- **Donut Mode** - Fullscreen spinning ASCII donut (Andy Sloane's donut.c geometry) rendered entirely in theme colors. 5 shade modes via `B`/`V` — Smooth, Glow, Bold, Dim, and Iced (pink icing on upward-facing surfaces with golden dough)
- **1-6 Lamps** - Display multiple lava lamps side by side
- **5 Sizes** - 11.5", 14.5", 16.3", 17", and 27" Grande (default)
- **Freestyle Mode** - Fullscreen lava with no lamp frame, filling the entire terminal
- **Groovy Animated Menu** - Lava background, rotating taglines, live lamp preview panel (every selection renders a real miniature lamp or koi pond next to the menu), inline theme palette swatch, position counters, `R` for randomize, `1`–`5` to jump between fields
- **Direct-launch CLI flags** - `lavacli --style koipond --theme koi_pond --duration 600` skips the menu entirely — perfect for tmux startup scripts and terminal screensavers
- **Rim/Edge Glow** - Dual-threshold rendering gives lava blobs a glowing halo edge
- **Resizable** - Lamps adapt when you resize the terminal
- **Half-Block Rendering** - Uses Unicode `▀▄█` characters for 2x vertical resolution
- **Metaball Physics** - Real metaball field simulation for authentic blob merging/splitting
- **Perlin Noise Flow** - Pure-Python 3D Perlin noise with fractal Brownian motion for smooth organic liquid animation
- **Heat/Buoyancy Cycle** - Blobs heat at the bottom, rise, cool at the top, and sink back down
- **Dark Metallic Base** - Hourglass-shaped base with 3-tone shading, matching classic black lava lamp bases
- **Rocket Style** - Mathmos Telstar-inspired rocket ship with cylindrical chrome glass column, sharp pointed nose cone, three swept-back fins, and a vertical chrome highlight stripe for polished metal feel
- **Interactive Controls** - Change speed, pause, cycle colors, add/remove blobs, return to menu, toggle HUD

## Install

The PyPI package is named **`pylavalamp`** (the bare `lavacli` name was already taken on PyPI), but the installed command is still `lavacli`.

```bash
pipx install pylavalamp
```

That's it — `lavacli` is now available as a command from anywhere in your terminal.

To install from a local clone instead:

```bash
git clone https://github.com/ElysiumDisc/lavacli.git
pipx install ./lavacli
```

For development (editable mode, source changes take effect immediately):

```bash
pipx install -e ./lavacli
```

### Uninstall

```bash
pipx uninstall pylavalamp
```

## Quick Start

```bash
lavacli
```

Or run directly without installing:

```bash
python3 -m lavacli
```

## CLI Flags (skip the menu)

Pass any lamp-config flag and the menu is skipped — LavaCLI drops straight into the animation. Omitted fields get sensible defaults. Great for tmux startup scripts, shell aliases, and terminal screensavers.

```bash
# Fullscreen koi pond with the matching theme
lavacli --style koipond --theme koi_pond

# Three swirling rocket lamps on the Purple Haze theme
lavacli --style rocket --flow swirl --theme purple_haze --count 3

# Surprise me, but keep it freestyle, for 10 minutes then exit
lavacli --random --style freestyle --duration 600

# Just randomize everything
lavacli --random

# Cozy campfire scene (pine forest + rising embers)
lavacli --style campfire

# Cozy fireplace with Aurora-night-sky embers
lavacli --style fireplace --theme aurora

# Christmas indoor fireplace
lavacli --style xmas

# Classic bi-color lamp: yellow/red mixed with blue/white
lavacli --theme yellow_red --bicolor blue_white

# Big spinning donut
lavacli --style donut
```

| Flag | Values | Description |
|------|--------|-------------|
| `--style` | `classic`, `slim`, `globe`, `lava`, `diamond`, `cylinder`, `pear`, `rocket`, `freestyle`, `koipond`, `fireplace`, `campfire`, `donut`, `xmas` | Lamp style |
| `--theme` | `yellow_red`, `blue_white`, `clear_orange`, `purple_haze`, `neon_green`, `blue_purple`, `clear_red`, `sunset`, `psychedelic`, `mono`, `koi_pond`, `aurora`, `campfire`, `cyberpunk`, `matrix`, `oceanic`, `xmas` | Color theme |
| `--flow` | `classic`, `chaotic`, `zen`, `bouncy`, `swirl`, `liquid` | Flow physics |
| `--count` | `1`–`6` | Number of lamps side by side |
| `--size` | `S`, `M`, `L`, `XL`, `G` | 11.5" / 14.5" / 16.3" / 17" / 27" Grande |
| `--random` | — | Randomize any unspecified fields |
| `--duration SECONDS` | integer | Run for N seconds then exit (screensaver mode) |
| `--bicolor THEME_B` | any `--theme` value | Mix a second palette into the lava (90s bi-color lamp) |
| `--version` | — | Print the installed version |

Run `lavacli --help` for the full list.

## Controls

### Menu

| Key | Action |
|-----|--------|
| `Up/Down` or `j/k` | Navigate between fields (wraps at the ends) |
| `Left/Right` or `h/l` | Cycle the selected field's value |
| `1`–`6` | Jump directly to STYLE / THEME / FLOW / COUNT / SIZE / TINT |
| `R` | Randomize all six fields |
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
| `B` | Add a blob (fish in Koi Pond; next sprinkle pattern in Donut) |
| `V` | Remove a blob (fish in Koi Pond; previous sprinkle pattern in Donut) |
| `T` | Toggle slow-shutter trails (motion blur) — lamp & fullscreen modes |
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
| Rocket | Mathmos Telstar rocket ship — cylindrical chrome body, pointed nose, three swept fins, chrome highlight stripe |
| Freestyle | No lamp frame - fullscreen lava fills the terminal |
| Koi Pond | Fullscreen animated koi pond with sage-green lily pads and colorized swimming fish |
| Fireplace | Fullscreen rising embers — hot metaballs spawn at the bottom, drift upward with flicker, cool and fade at the top, then recycle |
| Campfire | Fullscreen campfire with pine forest scene — same ember physics as Fireplace, always renders the layered conifer silhouette background with starry sky |
| Donut | Fullscreen spinning ASCII donut (Andy Sloane's donut.c) rendered in theme colors; 5 shade modes via `B`/`V` |
| Christmas | Fullscreen indoor Christmas fireplace — brick surround, wooden mantel, two stockings, procedural dancing hearth flame (white-hot core → orange → red → dark, with flicker), ember physics on top, stone hearth, hardwood floor |

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
| Koi Pond | White-salmon-orange koi gradient | Teal water (pairs with lily pads) |
| Aurora | Violet-magenta-green-cyan ribbons | Near-black night sky (pairs with Fireplace) |
| Campfire | Dark ember glow → red → orange → golden yellow core | Black night sky |
| Cyberpunk | Neon pink and cyan | Black |
| Matrix | Digital neon greens | Black |
| Oceanic | Deep sea blues and cyans | Dark navy |

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

Each fish has 14 connected body segments with constraint-based movement, sinusoidal swimming undulation, pectoral fins, and a fanning tail fin. The pond surface is decorated with 6-10 sage-green elliptical lily pads (each with a characteristic V-notch and 3-tone shading) — fish swim freely over and around them, just like a real koi pond. Fish are colorized using 6 real koi varieties:

| Variety | Colors |
|---------|--------|
| Kohaku | Orange-red markings on white body |
| Sanke | Red patches on white with black accents |
| Showa | Red and white on black body |
| Tancho | Red crown on clean white body |
| Ogon | Solid metallic gold |
| Asagi | Blue-gray back with orange belly |

The pond is biased toward Kohaku and Sanke (white-with-orange) so the default scene reads as a classic watercolor koi pond. Pick the **Koi Pond** theme for the closest match to that aesthetic — teal water + sage lily pads + warm koi colors. Lily pads stay sage-green regardless of which theme you cycle to. Use `B`/`V` to add/remove fish, and `C` to cycle themes.

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

- Python 3.8+
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

The metallic base and cap are rendered as filled shapes using half-block characters with 3-tone highlight/mid/shadow shading. The base uses a classic hourglass profile. The rocket style uses a sharp pointed nose cone, a serrated three-fin base profile, and an extra horizontal chrome highlight stripe down the center column for polished metal curvature.

### Fireplace

The Fireplace style reuses the metaball engine but flips gravity: a dense cloud of small "embers" spawns at the bottom and drifts upward. Each ember's temperature decays as a function of its height and its horizontal distance from the center, forming a natural triangular flame shape. The base of the fire features a high-fidelity **procedural 3D log structure**—complete with 3D-shaded bark, concentric rings on log ends, glowing cracks, and a bed of hot ash. A **sustained procedural flame core** sways and tapers upwards from the logs, providing a solid body of fire. When using the **Campfire theme**, a lush **pine tree silhouette background** with layered conifers, rolling hills, and stars is procedurally rendered behind the fire structure.


### Bi-color Lava

Each ball carries a `palette_id` (0 or 1); `--bicolor THEME_B` assigns palettes round-robin so the two halves stay balanced. At every rendered pixel the engine sums per-palette metaball contributions separately and picks the dominant palette for coloring, so merged blobs blend along a natural boundary. Cross-palette color pairs are allocated lazily on first use via `ColorHelper.set_secondary_theme` — only the (fg, bg) combos that actually appear on screen consume curses pair slots, which keeps the approach well within the 256-pair budget on standard terminals. Bi-color is a metaball-only effect; the Perlin-noise `liquid` flow has no per-ball identity and falls back to the primary palette.

### Motion Trails

When `T` is pressed, each lamp allocates a per-cell trail buffer sized to the body. Every frame, cells that currently hold lava refresh to full trail life; cells that went back to liquid but still have life remaining are redrawn with a progressively dimmer level (lava 3 → 2 → 1 → rim) over ~14 frames before disappearing. The trail buffer lives on the `Lamp` instance, so resize or reset cleanly invalidates it.

### Donut

The donut is a port of Andy Sloane's classic donut.c: a torus of inner radius 1 and outer radius 2 is rotated about two axes, perspective-projected, lit by a diagonal Lambertian light, and rasterized into a z-buffer. Instead of donut.c's 12-character luminance ramp, each lit surface point picks its palette from `THEME_ORDER` using a mix of its `(i, j)` angular indices and a slowly advancing frame offset, then the Lambertian intensity selects the shade within that palette. The whole donut visibly rotates through every color theme as it spins, and `B`/`V` switches between 8 sprinkle patterns (solid cycle, ring bands, tube stripes, confetti grid, chunky wedges, stacked hoops, fine speckle). Width and height scale independently so the donut fills wide terminals too — on an 80×24 screen the silhouette diameter spans ~60 columns. `ColorHelper.setup_donut_colors()` pre-warms curses pairs for every theme's lava palette against the current liquid background, so sprinkles never fall back to the liquid-on-liquid pair mid-render.

### Koi Pond

The koi pond is a separate render path from the lava lamp. Each fish is a 14-segment chain with constraint-based segment physics — the head moves toward a random target with a sinusoidal lateral wobble, and the rest of the body trails behind via distance constraints. Lily pads are scattered with Poisson-ish rejection sampling, rasterized as ellipses with a V-notch carved out, and stamped into the render buffer *before* fish so the koi naturally swim over them. The whole scene uses the same half-block buffer rendering as the lava lamp.

## License

MIT
