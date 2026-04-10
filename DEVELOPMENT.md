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

## Packaging & Releasing

LavaCLI is published to PyPI as **`pylavalamp`** (the bare `lavacli` name was already taken). The GitHub repo and the installed console command are still `lavacli` — only the PyPI distribution name differs.

| What | Name |
|---|---|
| GitHub repo | `https://github.com/ElysiumDisc/lavacli` |
| PyPI distribution | `https://pypi.org/project/pylavalamp/` |
| Installed console command | `lavacli` (from `[project.scripts]` in `pyproject.toml`) |

All packaging metadata lives in `pyproject.toml`. Build/upload tools (`build`, `twine`) are run through `pipx run` so nothing pollutes your global Python.

### One-time setup

Only needed the first time you publish from a given machine.

```bash
sudo apt install pipx          # or: brew install pipx
```

1. Register at https://pypi.org/account/register/ and enable 2FA (PyPI requires it for uploads).
2. Create an API token at https://pypi.org/manage/account/token/. For a first-time publish of a new name, scope must be **Entire account** (the project doesn't exist on PyPI yet to scope to). Copy the token — PyPI only shows it once.
3. Save the token in `~/.pypirc`:

   ```bash
   nano ~/.pypirc
   ```

   Paste:

   ```ini
   [pypi]
     username = __token__
     password = pypi-PASTE-YOUR-REAL-TOKEN-HERE
   ```

   Save with **Ctrl+O**, **Enter**, **Ctrl+X**.

4. Lock the file down so no other user on the machine can read it:

   ```bash
   chmod 600 ~/.pypirc
   ls -la ~/.pypirc          # should show -rw-------
   ```

5. To verify the structure without printing the token:

   ```bash
   grep -v password ~/.pypirc
   ```

### Code-only update (push to GitHub without releasing a new PyPI version)

If you're just iterating on code, fixing typos, updating docs, etc., and don't want to cut a new PyPI release yet:

```bash
git add <files>
git commit -m "<what changed>"
git push origin main
```

That's it. PyPI is unaffected — users still get the last published version with `pipx install pylavalamp`.

### Releasing a new version (GitHub + PyPI)

The full release loop, every time:

1. **Bump the version** in `pyproject.toml`. SemVer:

   | Change | Bump | Example |
   |---|---|---|
   | Bug fix only | patch | `1.2.0` → `1.2.1` |
   | New feature, backward-compatible | minor | `1.2.0` → `1.3.0` |
   | Breaking change | major | `1.2.0` → `2.0.0` |

2. **Add a CHANGELOG entry** at the top of `CHANGELOG.md`:

   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD

   ### Added
   - ...

   ### Changed
   - ...

   ### Fixed
   - ...
   ```

   Use only the subsections that apply.

3. **Clean stale build artifacts.** PyPI rejects duplicate filenames, so old `dist/` files will conflict:

   ```bash
   rm -rf dist/ build/ *.egg-info/
   ```

4. **Build, validate, upload:**

   ```bash
   pipx run build --sdist --wheel
   pipx run twine check dist/*
   pipx run twine upload dist/*
   ```

   `twine check` must report `PASSED` on both files. Then `twine upload` reads `~/.pypirc` automatically and ships to PyPI. The success output ends with `View at: https://pypi.org/project/pylavalamp/X.Y.Z/`.

5. **Verify the new version installs:**

   ```bash
   pipx upgrade pylavalamp     # for users who already have it
   lavacli                     # smoke-test
   ```

6. **Commit and tag in git:**

   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Release vX.Y.Z"
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin main --tags
   ```

   The annotated tag is a permanent marker pointing at the exact commit that produced the PyPI release. `git checkout vX.Y.Z` later shows precisely what shipped.

7. **Create the GitHub Release** (optional but tidy):
   1. Go to https://github.com/ElysiumDisc/lavacli/releases/new
   2. **Choose a tag**: pick the `vX.Y.Z` you just pushed
   3. **Release title**: `vX.Y.Z`
   4. **Description**: paste the matching section from `CHANGELOG.md`
   5. Click **Publish release**

   GitHub auto-generates a source tarball from the tag and links it under the release.

### Things you can't undo

**You cannot overwrite an existing version on PyPI.** If you upload `1.2.0` and notice a typo, your options are:

- **Bump and re-upload** — fix it, bump to `1.2.1`, repeat the release loop. Your version history will have a dead `1.2.0` in it forever.
- **Yank the bad version** — at `https://pypi.org/manage/project/pylavalamp/release/X.Y.Z/`, click **Yank**. Yanking is *not* deletion: yanked versions remain installable for anyone who pinned them, but `pipx install pylavalamp` (unpinned) will skip them.

This is why `twine check` and the local wheel test exist — catch problems before the version number is burned.

### What lives where

| Path | Purpose | Commit? |
|---|---|---|
| `pyproject.toml` | Build config + PyPI metadata (name, version, classifiers, URLs) | yes |
| `CHANGELOG.md` | Per-version release notes | yes |
| `dist/` | Built wheel + sdist (output of `build`) | no — gitignored |
| `build/` | setuptools scratch dir | no — gitignored |
| `*.egg-info/` | setuptools metadata cache | no — gitignored |
| `~/.pypirc` | Your PyPI token | **never commit** — lives in `$HOME`, `chmod 600` |

### Troubleshooting packaging

| Symptom | Cause | Fix |
|---|---|---|
| `400 File already exists` on upload | Forgot to bump the version, or `dist/` still has old artifacts | Bump version in `pyproject.toml`, `rm -rf dist/`, rebuild, re-upload |
| `403 Invalid or non-existent authentication` | `~/.pypirc` token is wrong, expired, or under the wrong section header | Regenerate the token at https://pypi.org/manage/account/token/ and update `~/.pypirc` |
| `twine check` fails on README rendering | README has Markdown PyPI's renderer doesn't accept | Render locally to see exactly what fails: `pipx run --spec 'readme_renderer[md]' python -m readme_renderer README.md -o /tmp/out.html` |
| Wheel installs but `lavacli` command not found | `[project.scripts]` entry missing or wrong | Check `pyproject.toml` has `lavacli = "lavacli.app:run"` under `[project.scripts]` |
| Classifier rejected | Trove classifier string doesn't exist verbatim | Validate against the official list: `pipx run --spec trove-classifiers python -c "from trove_classifiers import classifiers; print('YOUR_STRING' in classifiers)"` |
| Build picks up `dist/` or `build/` as a package | Missing `[tool.setuptools] packages = [...]` block | Already set in `pyproject.toml` — don't remove it |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Terminal too small` | Resize terminal to at least 46x20 |
| No colors / garbled output | Ensure `TERM` is set to `xterm-256color` or similar |
| Unicode boxes instead of smooth blobs | Terminal needs Unicode support; try a modern emulator |
| Flickering | Try reducing lamp count or using a GPU-accelerated terminal |
| Import error on Windows | Install `windows-curses`: `pip install windows-curses` |
| Liquid flow too slow | Reduce terminal size or increase `noise_speed` parameter |
