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
│   ├── pond.py                 # Koi pond: Fish/Pond classes, skeletal physics, rendering
│   └── themes.py               # Color themes, koi patterns, and ColorHelper class
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
| `app.py` | Curses setup, animation loop (~20fps), input dispatch, layout, resize handling, menu-to-lamp/pond flow |
| `lamp.py` | Core lava simulation: shape profiles (including rocket), `Ball`/`Lamp` classes, metaball field computation, Perlin noise field, half-block rendering, solid base/cap/frame rendering |
| `pond.py` | Koi pond simulation: `Segment`/`Fish`/`LilyPad`/`Pond` classes, skeletal segment physics, lily pad rasterization with V-notch + 3-tone shading, buffer-based fish body rasterization, pectoral fin and tail fin rendering |
| `noise.py` | Pure-Python 3D Perlin noise implementation with fractal Brownian motion (FBM) for the Liquid flow type |
| `themes.py` | 11 theme definitions (classic Lava Library colors + Koi Pond, all with dark bases and sage lily pad palette), 6 koi color patterns, `ColorHelper` for curses color pair management, frame/base/cell/pond drawing methods |
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

10 styles available:

| Style | Shape | Profile |
|-------|-------|---------|
| Classic | Conical (narrow top, wide bottom) | `SHAPES['classic']` |
| Slim | Straighter taper | `SHAPES['slim']` |
| Globe | Bulbous, wider at top | `SHAPES['globe']` |
| Lava | Organic wavy | `SHAPES['lava']` |
| Diamond | Angular, widest at center | `SHAPES['diamond']` |
| Cylinder | Straight tube, flat sides | `SHAPES['cylinder']` + `CYLINDER_CAP_PROFILE` + `CYLINDER_BASE_PROFILE` |
| Pear | Bulbous belly, narrow neck | `SHAPES['pear']` |
| Rocket | Cylindrical chrome glass column with sharp nose cone, three swept fins (serrated profile), and chrome highlight stripe | `SHAPES['rocket']` + `ROCKET_CAP_PROFILE` + `ROCKET_BASE_PROFILE` + `Lamp._chrome_shade()` |
| Freestyle | Full-width rectangle | `SHAPES['freestyle']` (no frame) |
| Koi Pond | Fullscreen animated fish | `SHAPES['koipond']` (dispatches to `pond.py`) |

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

### Koi Pond System (pond.py)

When the user selects "Koi Pond" style, `app.py` dispatches to `_run_pond()` instead of `_run_lamp()`. The pond system is entirely separate from the lava simulation.

**Fish anatomy (14 segments):**

```
Seg:  0    1    2    3    4    5    6    7    8    9   10   11   12   13
      snout head neck shoulder ---- body ----  taper peduncle  tail fin
Width: 0.6  1.4  2.6  3.8  4.8  5.2  5.0  4.4  3.4  2.2  1.2  0.8  2.4  3.6
```

- Segments 4-5 have pectoral fin extensions (extra width beyond body edge)
- Segments 12-13 fan out to form the tail fin
- Segments 10-11 form the narrow caudal peduncle (creates the classic fish body-to-tail narrowing)

**Movement:** Each fish swims toward a random target point. The head moves along the direction vector with a sinusoidal lateral displacement (period=48 frames) for natural undulation. Each subsequent segment is constrained to stay within `SEGMENT_LENGTH` (3.2 units) of its predecessor, creating a trailing chain effect.

**Rendering:** Buffer-based rasterization into a 2D grid at half-block resolution (`height * 2` physical rows). For each segment, cells within the body width are stamped perpendicular to the local spine direction. Spine interpolation between segments fills gaps. The buffer is then drawn using `ColorHelper.draw_pond_cell()` with the same half-block technique as the lava lamp.

**Color patterns:** 6 koi varieties defined in `themes.py` (`KOI_PATTERNS`), each with per-body-part colors (head, body_main, body_accent, fin, tail). `ColorHelper.setup_pond_colors()` allocates fish-on-water, fish-on-fish, and lily-pad-on-water color pairs. `_resolve_fish_color()` maps segment index and distance-from-center to the appropriate body part color, and also recognizes `('pad', shade)` cells (shade in `'rim'`/`'fill'`/`'shadow'`) to return one of the three sage-green pad colors from the active theme.

**Lily pads:** `Pond._init_lily_pads()` scatters 6-10 elliptical pads across the pond using Poisson-ish rejection sampling (rejecting positions too close to existing pads). Pad count and size scale with pond dimensions, and pads are regenerated on terminal resize. Each pad has a center, two radii, and a notch angle. `_stamp_lily_pad()` rasterizes the ellipse, carves out a small angular wedge for the V-notch, and tags cells with `('pad', shade)` where shade is `'rim'` near the edge, `'shadow'` inside a small offset patch, and `'fill'` everywhere else. Pad cells are stamped *before* fish so fish naturally render on top. `_fill_width` and `_fill_fin` explicitly overwrite pad cells when rasterizing fish bodies (otherwise they would IndexError on the 2-tuple pad cells).

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
    'lily_pad': 65,                  # sage green for koi pond lily pads
    'lily_pad_dark': 22,             # darker shadow patch on pads
    'lily_pad_rim': 107,             # lighter pad rim
},
```

Then add `'my_theme'` to `THEME_ORDER`. The lily pad colors only apply when the user picks Koi Pond mode; using sage-green across all themes keeps the pond visually recognizable regardless of the lava theme.

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

## Adding a New Koi Pattern

In `themes.py`, add to the `KOI_PATTERNS` dict:

```python
'my_koi': {
    'name': 'My Koi',
    'head': 196,          # ANSI 256-color code for head/snout
    'body_main': 231,     # primary body color
    'body_accent': 202,   # secondary body color (patches)
    'fin': 252,           # pectoral fin color
    'tail': 248,          # tail fin color
},
```

The pattern is automatically available to fish. `_resolve_fish_color()` maps segment positions to body parts: segments 0-1 use `head`, 2-9 alternate `body_main`/`body_accent`, 4-5 outer edges use `fin`, 10-11 use `body_main`, 12-13 use `tail`.

## Packaging & Releasing to PyPI

LavaCLI is published to PyPI under the distribution name **`pylavalamp`** (the bare `lavacli` name was already taken). The console script and the GitHub repo are still called `lavacli` — only the PyPI package name differs. All packaging metadata lives in `pyproject.toml`.

### One-time setup

```bash
# Make sure pipx is installed (we use `pipx run` for ephemeral build/twine,
# so nothing has to live in your global Python).
sudo apt install pipx        # Debian/Ubuntu
brew install pipx            # macOS

# Create accounts and enable 2FA on:
#   https://test.pypi.org/account/register/   (TestPyPI - dry runs)
#   https://pypi.org/account/register/        (real PyPI)
# Generate an API token for each one (Account Settings -> API tokens).
# Save them in ~/.pypirc:
cat > ~/.pypirc <<'EOF'
[pypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmcC...    # your real PyPI token

[testpypi]
  repository = https://test.pypi.org/legacy/
  username = __token__
  password = pypi-AgENdGVzdC5weXBpLm9yZwI...   # your TestPyPI token
EOF
chmod 600 ~/.pypirc
```

### Release workflow

The whole release loop is four commands. Run them from the repo root.

#### 1. Bump the version

Edit `pyproject.toml` and bump `version = "X.Y.Z"`. Follow [SemVer](https://semver.org/):

| Change | Bump |
|---|---|
| Bug fix only | patch (`1.2.0` -> `1.2.1`) |
| New feature, backward-compatible | minor (`1.2.0` -> `1.3.0`) |
| Breaking change | major (`1.2.0` -> `2.0.0`) |

Then add a matching entry to the top of `CHANGELOG.md` describing what changed (Added / Changed / Fixed / Removed).

#### 2. Clean previous build artifacts

Stale files in `dist/` will get re-uploaded by twine and PyPI rejects duplicates, so always wipe them first:

```bash
rm -rf dist/ build/ *.egg-info/ pylavalamp.egg-info/
```

(`dist/`, `build/`, and `*.egg-info/` are already in `.gitignore`.)

#### 3. Build the wheel and sdist

```bash
pipx run build --sdist --wheel
```

This produces two files in `dist/`:

- `pylavalamp-X.Y.Z-py3-none-any.whl` — the **wheel**, what `pipx install` downloads. Pre-built, fast install.
- `pylavalamp-X.Y.Z.tar.gz` — the **sdist** (source distribution), the source code as a tarball. PyPI requires both.

#### 4. Validate the metadata

```bash
pipx run twine check dist/*
```

Both files should report `PASSED`. If you get warnings about README rendering or missing fields, fix `pyproject.toml` and rebuild before uploading — once a version is on PyPI you cannot replace it, you can only yank it and bump the version again.

#### 5. (Recommended) Dry-run on TestPyPI first

```bash
pipx run twine upload -r testpypi dist/*
```

Then verify the listing renders correctly at `https://test.pypi.org/project/pylavalamp/` and try installing it:

```bash
pipx install --index-url https://test.pypi.org/simple/ pylavalamp
lavacli   # smoke-test the installed command
pipx uninstall pylavalamp
```

#### 6. Upload to real PyPI

```bash
pipx run twine upload dist/*
```

Verify at `https://pypi.org/project/pylavalamp/` and test the real install:

```bash
pipx install pylavalamp
lavacli
```

#### 7. Tag the release in git

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Release vX.Y.Z"
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin main --tags
```

### Updating an already-published release

**You cannot overwrite an existing version on PyPI.** If you discover a bug after uploading `1.2.0`, the workflow is:

1. Fix the bug.
2. Bump to `1.2.1` in `pyproject.toml`.
3. Add a CHANGELOG entry.
4. Repeat steps 2-7 above.

If a release is genuinely broken (e.g. missing files, wrong dependencies), you can [**yank**](https://pypi.org/help/#yanked) it via the PyPI web UI — yanked versions stay installable for anyone who pinned them but no longer satisfy unpinned `pipx install pylavalamp` requests. Yanking is *not* deletion; it's a "use the next version instead" signal.

### What lives where

| Path | Purpose | Commit? |
|---|---|---|
| `pyproject.toml` | Build config + PyPI metadata (name, version, classifiers, URLs) | yes |
| `dist/` | Built wheel + sdist (output of `build`) | no - gitignored |
| `build/` | setuptools scratch dir | no - gitignored |
| `*.egg-info/` | setuptools metadata cache | no - gitignored |
| `~/.pypirc` | Your PyPI/TestPyPI tokens | **never commit** - lives in $HOME |

### Troubleshooting packaging

| Symptom | Fix |
|---|---|
| `twine check` fails on README rendering | The `readme = "README.md"` field in `pyproject.toml` points at the file PyPI renders. Make sure it's valid Markdown. |
| `400 File already exists` on upload | You forgot to bump the version, or `dist/` still has the old artifacts. `rm -rf dist/` and rebuild after bumping. |
| `403 Invalid or non-existent authentication` | Your `~/.pypirc` token is wrong or expired. Generate a new one from your PyPI account settings. |
| Wheel installs but `lavacli` command not found | Check `[project.scripts] lavacli = "lavacli.app:run"` in `pyproject.toml` — the entry point is what creates the command. |
| `pip install pylavalamp` works but `pipx` doesn't | `pipx` requires the package to expose at least one console script. The `[project.scripts]` block above satisfies that. |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Terminal too small` | Resize terminal to at least 46x20 |
| No colors / garbled output | Ensure `TERM` is set to `xterm-256color` or similar |
| Unicode boxes instead of smooth blobs | Terminal needs Unicode support; try a modern emulator |
| Flickering | Try reducing lamp count or using a GPU-accelerated terminal |
| Import error on Windows | Install `windows-curses`: `pip install windows-curses` |
| Liquid flow too slow | Reduce terminal size or increase `noise_speed` parameter |
