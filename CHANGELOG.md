# Changelog

All notable changes to LavaCLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [2.2.0] - 2026-05-28

A focused follow-up bug-hunt over the `resize()` path, prompted by a fresh top-to-bottom audit of all eight modules (two independent adversarial passes). It surfaced a single root-cause pattern — a resize handler that rescales metaball *positions* but forgets the metaball *radius* — present in two places. Both are visual-only (no crash); SemVer-wise these are patch-level fixes, released as `2.2.0` per request. Severity tags (`[H#]`, `[M#]`) match the archived audit so the trail back to the analysis is clear.

### Fixed

- **Lava blobs didn't rescale on terminal resize** (`lamp.py` — H1) - `Lamp.resize()` updated `self.ball_radius` (the default used by `add_ball`) and rescaled each ball's `x`/`y`, but never updated the existing balls' `.radius` / `.radius_sq`. Because the metaball field reads `ball.radius_sq`, blobs kept their pre-resize pixel size while the lamp geometry changed around them — and any ball added *after* a resize used the new radius, so a single lamp could end up with mismatched blob sizes. Existing balls now scale by the same ratio applied to the default, preserving per-ball size differences (e.g. fireplace embers spawned at `0.6×`).
- **Menu background lava didn't rescale on resize** (`menu.py` — M1) - Same pattern in `_MenuLava.resize()`: ball positions were rescaled but `radius_sq` was left stale, so `field_at_dual` painted weaker background blobs after a window resize. The radius is now recomputed from the new width (matching `__init__`'s `max(3.0, width * 0.15)` sizing).

### Documentation

- **Audit archived** - The audit driving this release lives at `~/.claude/plans/virtual-frolicking-gray.md`, with the same `H#`/`M#` tags used above. It records both the two findings and the larger set of paths that were traced and confirmed correct (divide-by-zero guards, trail-buffer sentinels, bicolor lazy color-pair allocation, donut z-buffer indexing, color-pair lifecycle, Perlin bounds).

## [2.1.0] - 2026-05-20

A bug-hunt + performance pass driven by a top-to-bottom audit of the render hot path. Every change is bound to a specific finding from `bug-hunt-code-performance-dreamy-frog.md`; severity tags (`[H#]`, `[M#]`, `[L#]`) match that report so the trail back to the original analysis is clear.

### Fixed

- **Bicolor + `--flow liquid` produced only palette A** (`lamp.py` — H1) - The liquid-flow branch of the bicolor field path hard-coded `palette_id = 0`, so the secondary palette was silently never selected and the lamp rendered as mono. Bicolor liquid now uses a smooth time-varying spatial mask (`sin(t * 0.5 + px * 0.18 + py * 0.13)`) to divide the noise field into palette A / B regions, so both palettes actually appear and drift across the lamp over time.
- **Fireplace bicolor pillar always rendered as palette A** (`lamp.py` — H2) - The central flame pillar's contribution was added only to `sum_at`, biasing the dominant-palette calculation and forcing the spine of every fireplace into the primary palette regardless of how the surrounding embers were colored. The pillar now splits its contribution 50/50 between the two palette sums, so the spine inherits whichever palette dominates among nearby embers (i.e. fireplaces actually look bicolor now).
- **Trail buffer collapsed the `-1` "outside glass" sentinel to `0`** (`lamp.py` — H3 / M10) - `entry[0] = tl if tl > 0 else 0` rewrote the out-of-glass sentinel as liquid, which could paint faint liquid color past the glass curve on the frame after a resize. The freestyle and `_render_body` trail paths also diverged subtly. Both paths now share a single `_apply_trail(...)` helper that preserves the sentinel end-to-end and re-asserts it from the live glass bounds when painting a ghost.
- **Donut and pond `R` reset discarded user state** (`app.py` — H7) - Pressing `R` rebuilt a fresh `Donut` / `Pond` with default `paused` / `shade_mode`. Now matches the lamp reset behavior introduced in 2.0.0: the previous instance's tunable state is carried over onto the new one.
- **`--duration` clock ticked during menu navigation** (`app.py` — H6) - The deadline was computed once before `show_menu()`, so time spent navigating fields counted against the lamp's runtime. A 30-second screensaver invocation could deliver a 5-second lamp if the user lingered in the menu. The deadline is now (re)computed at each animation launch, so the duration always applies to the running scene, never the menu — and surviving across menu→anim→menu cycles can no longer silently shorten the next session.
- **`--bicolor` silently swallowed on `--style koipond` / `donut`** (`app.py` — M7) - Pond and donut ignore bicolor at render time. The flag is now normalized to `None` for those styles in `_config_from_args`, so the config dict no longer carries a setting that downstream code can't act on.
- **`change_theme` left scene colors un-allocated** (`themes.py` — M2) - `change_theme()` cleared `_lazy_pair_cache` but did not re-seed it, so the first xmas / campfire frame after every `C`-press paid for a burst of `init_pair` calls. `change_theme` now reinvokes `setup_scene_colors()` immediately so the first post-switch frame renders without a stall.

### Performance

- **Static campfire scene buffers** (`lamp.py` — H4) - `_get_forest_bg_color` and `_get_campfire_log_color` were called four times per cell per frame (top + bottom for both forest and logs) at ~6,000 cells × 20 fps = ~480k calls/sec, but their outputs are completely deterministic from `(px, py)`. They're now rasterized once into 2-D lookup tables (`_forest_buf`, `_log_buf`) at construction / resize and the per-frame call collapses to a list-of-list lookup. Campfire and fireplace styles render with a much flatter frame-time curve at large terminal sizes.
- **Pond render buffer reused in place** (`pond.py` — H5) - `render()` was building a fresh per-frame buffer via `[row[:] for row in self._pad_buf]`, allocating ~24,000 list cells per frame on modest terminals. The persistent `_render_buf` is now reset in place via slice assignment from the pad backdrop, eliminating the bulk of the GC churn from pond rendering.
- **Single unified `compute_field_cell`** (`lamp.py` — M4) - `compute_field_dual` and `compute_field_bicolor_dual` were near-duplicates differing only in the per-ball palette-sum branch — ~200 lines of duplicated body that had already drifted (H1, H2 lived in one but not the other). Collapsed into a single `compute_field_cell(px, py_t, py_b)` returning `(ft, t_pid, fb, b_pid)`, with the bicolor branch contained to a few lines inside the per-ball loop. Hot-path locals (`balls`, `cutoff_sq`, `noise_time*2`) are hoisted out of the loop.
- **`field_to_level` uses `bisect_right`** (`lamp.py` — M6) - The 6-step if-chain (called twice per cell) is now a single `bisect_right` against a 4-element threshold tuple, with the rim and liquid edge cases kept as inline guards.
- **Donut z/color buffers cleared via slice assignment** (`donut.py` — M3) - Replaced the per-frame Python `for i in range(n_cells)` clear with `z[:] = [neg_inf] * n_cells` and `col_buf[:] = [None] * n_cells`. Slice assignment runs in C and is ~10× faster at typical terminal sizes (~25k entries).
- **Single shared `ColorHelper` across menu ↔ anim** (`app.py`, `menu.py`, `themes.py` — M9) - `show_menu()` and the three runners each used to construct a fresh `ColorHelper` per call, re-init-pairing hundreds of curses pairs every time the user bounced between menu and lamp. A long screensaver-style session would creep `_next_pair_id` toward `COLOR_PAIRS` until `_lazy_color_pair` silently fell back to a neutral pair (visible as colors stopping refreshing). The helper is now constructed once in `_main` and threaded through `show_menu(ch=...)` and `_run_*(ch=...)`, with each entry point re-theming the helper in place. Pair-counter growth is bounded by the static allocation per theme, not the session length.
- **Liquid noise sampled once per cell instead of twice** (`lamp.py` — M5) - `compute_noise_field` was called separately for the top and bottom half-blocks of every cell — 42 `noise3` lookups per cell at 3 octaves. Top and bottom halves differ by only one physical unit, so the cell is now sampled once at the midpoint and reused for both halves. Visually indistinguishable at half-block resolution; `--flow liquid` now runs at roughly twice the previous frame rate.
- **Menu background skips occluded cells** (`menu.py` — M11) - `_render_bg` was running the metaball field math for every cell in the terminal even though most cells sit behind the opaque menu / preview box and are immediately overpainted. The call now accepts a list of skip rectangles (menu box and, when shown, preview box) and short-circuits cells inside them. On small terminals where the menu fills most of the screen, this halves menu frame cost.
- **`draw_colored_cell` no longer dict-looks-up the liquid color per cell** (`themes.py` — L3) - The donut's per-cell hot path repeatedly read `self.theme['liquid']`. Cached as `_liquid_color` on the helper, updated in `__init__` / `change_theme`.

### Internal

- **Stronger forest tree hash** (`lamp.py` — L1) - The old `(idx * 17 ^ idx * 31) % 100` mixer produced visibly regular spacing patterns because the two terms shared the same `idx` factor, and the three forest layers were perfectly correlated with each other. Replaced with a 32-bit integer mixer keyed on `(layer_idx, idx)` (Knuth's `2654435761` multiplier XOR'd with a Wichmann-Hill-derived layer term), which decorrelates both the in-layer spacing and the three depth bands. Cosmetic only — campfire forest looks more natural.

### Documentation

- **Audit report archived** - The full audit (24 findings, severity-tagged) that drove this release lives at `~/.claude/plans/bug-hunt-code-performance-dreamy-frog.md`. Future maintenance can map any item back to the original analysis via the H#/M#/L# tags used above.

## [2.0.0] - 2026-05-16

This is a stability + performance release that also consolidates accumulated polish. The major-version bump reflects the cumulative reach across modules (lamp/donut/pond/app) rather than a single breaking change — there is no CLI/menu surface change in this release.

### Fixed

- **Crash on terminal resize across all three animation modes** (`app.py`) - The three `_handle_key` closures in `_run_lamp`, `_run_donut`, and `_run_pond` each referenced an undefined `scr` instead of the enclosing `screen` parameter when handling `curses.KEY_RESIZE`. The first window resize while an animation was running raised `NameError`, taking down the curses session. All three sites now correctly use `screen.getmaxyx()`.
- **Pond resize could divide by zero on `target_x` / `target_y` recompute** (`pond.py`) - `Pond.resize()` correctly guarded `old_w == 0` and `old_ph == 0` when scaling fish segment positions, but the very next block scaled each fish's `target_x` / `target_y` without the same guard. Pulled the divisions into the same ternary-guarded form so resizes from a zero-dim pond no longer crash.
- **Lamp reset lost user-tuned state** (`app.py`) - Pressing `R` in a lamp animation rebuilt every `Lamp` with default `speed_mult` / `trails` / `paused` / `flame_size`, silently discarding the user's tuning. Now matches donut behavior: the previous lamp's state is captured and restored onto the new instances.
- **Initial pond fish spawned in a deterministic pattern cycle** (`pond.py`) - `_init_fish` selected each fish's pattern via `weighted[i % len(weighted)]`, producing the same visual sequence every launch whenever `fish_count > len(weighted)`. Now uses `random.choice(weighted)`, matching the behavior of `add_fish`.

### Performance

- **`compute_body_screen_bounds` memoized** (`lamp.py`) - The per-row column-bounds list is fully determined by `body_width` and the static profile, but it was being recomputed every frame inside `Lamp.render`. Now cached on the instance and invalidated in `resize()`, eliminating one full profile-interpolation pass per frame.
- **Cap / base render hoists out of the row loop** (`lamp.py`) - `_render_cap` and `_render_base` were re-evaluating `_get_cap_profile()` / `_get_base_profile()`, the `_denom` constant, `body_top_w / 2` (or `body_width / 2`), and the rocket-style flag on every row even though all four are invariant for the duration of a single render call. Lifted them above the `for row` loop.
- **Fireplace metaball `math.sin` collapsed** (`lamp.py`) - In `compute_field_dual` and `compute_field_bicolor_dual`, the asymmetric teardrop sway `math.sin(noise_time * 2 + ball.x * 0.5)` was being recomputed separately in the top-half and bottom-half branches even though the argument is identical for both. Hoisted to a single `sway` local per ball, plus `noise_time * 2.0` lifted out of the per-ball loop entirely.
- **Donut `BOLD_MAP` no longer reallocated per frame** (`donut.py`) - The 5-tuple lived inside `Donut.render()` and was rebuilt on every frame; promoted to a module-level constant.
- **Donut theme switch no longer copies the palette** (`donut.py`) - `set_theme()` was wrapping `t['lava']` in `list()`, allocating a new 5-element list every theme change. The palette is read-only, so the underlying tuple is now used directly.

### Internal

- **`show_hud` is no longer leaked into the shared state dict** (`app.py`) - `_run_animation` was using `state.setdefault('show_hud', True)` then toggling a local `show_hud` that diverged from the dict entry. The dict was never read elsewhere, but the divergence was a latent footgun. `show_hud` is now purely local to the loop.
- **`fireplace` style → theme coupling intentionally absent** (`app.py`) - `campfire` and `xmas` styles force their matching themes; `fireplace` does not, because it's a generic ember field that reads well under any palette. Documented inline to prevent future drift.
- **Misc readability** (`donut.py`) - Simplified the Glow-mode color clamp; added a one-line comment explaining `prev_shade`'s negative-modulo idiom.

## [1.10.0] - 2026-05-14

### Performance

- **Dual-field metaball optimization** (`lamp.py`, `menu.py`) - Implemented `compute_field_dual` and `compute_field_bicolor_dual` which calculate both top and bottom half-block field values in a single pass. Shared calculations (like `dx*dx`) are now performed once per cell rather than twice, significantly reducing the CPU load for the core rendering loop.
- **Distance-based metaball cutoff** (`lamp.py`) - Added a `METABALL_CUTOFF_SQ` threshold. The engine now skips calculating contributions from blobs further than 20 units away, providing a massive speedup for large lamp styles and high-resolution terminals.
- **Radius-squared caching** (`lamp.py`, `menu.py`) - Metaball radius squares are now pre-calculated on ball initialization, eliminating a multiplication operation from the inner loop of the field calculator.
- **Koi Pond background pre-rendering** (`pond.py`) - Static elements like lily pads are now pre-rendered into a persistent background buffer (`_pad_buf`) on initialization or resize. The main render loop now performs a fast row-copy of this buffer instead of re-evaluating elliptical geometry and notch logic for every pad on every frame.
- **Optimized chrome shading** (`lamp.py`) - Hoisted redundant calculations in `_chrome_shade` and simplified the rank-based scoring system for 3-tone curvature highlights.

## [1.9.0] - 2026-05-03

### Fixed

- **Color-pair counter leaked across theme cycles** (`themes.py`) - `ColorHelper.change_theme()` previously saved `_next_pair_id` before calling `setup()` and restored it afterward. This had the opposite of the intended effect: the counter monotonically grew toward `curses.COLOR_PAIRS` with every `C`-press, until `_lazy_color_pair` silently fell back to a neutral pair and new colors stopped appearing. The save/restore is removed; subsequent lazy allocations now overwrite orphaned IDs from the previous theme (safe — `init_pair` redefines on collision), so the counter stays bounded across arbitrary theme cycles.
- **Idle frames invoked the key handler with a sentinel** (`app.py`) - `_run_animation` used `elif key:` to dispatch input, but `screen.getch()` returns `-1` (truthy in Python) when its `timeout()` expires with no input. The handler was being called every idle frame with `key=-1`, paying a function-call cost for nothing. Now uses an explicit `elif key != -1:`, matching the menu's idle handling.
- **Koi pond weighted pattern list could empty** (`pond.py`) - `_init_fish` filtered the kohaku/sanke-weighted list against `KOI_PATTERN_NAMES`; if a future refactor renamed every weighted pattern, the filter could empty the list and `weighted[i % len(weighted)]` would raise `ZeroDivisionError`. Now falls back to `KOI_PATTERN_NAMES` (or `['kohaku']` as a last resort) before iterating.
- **`add_fish` ignored the visual-style weighting** (`pond.py`) - Pressing `B` in the pond appended a uniformly-random pattern via `random.choice(KOI_PATTERN_NAMES)`, gradually drifting the pond away from the kohaku/sanke bias used at startup. Both call sites now share a `_WEIGHTED_PATTERNS` module constant, so newly-added fish match the original visual mix.

### Performance

- **Row-only computations hoisted out of lamp render col loops** (`lamp.py`) - `_render_body`, `_render_cap`, and `_render_base` were re-evaluating `get_glass_bounds(py_t/py_b)` (and the cap/base profile interpolations) once per column even though their results depend only on the row. For a body 20 columns wide that was ~20× redundant work per row each frame; the calls are now hoisted above the inner `for col` loop.
- **Donut z-/color-buffer reset is now in-place** (`donut.py`) - `Donut.render` previously reset the buffers via `z[:] = [neg_inf] * n_cells` and `col_buf[:] = [None] * n_cells`, allocating two fresh per-frame lists the size of the terminal just to slice them in. Replaced with a single in-place fill loop, eliminating ~720 KB/sec of allocation churn at typical terminal sizes.
- **Lazy fish cross-pair allocation** (`themes.py`) - `setup_pond_colors` previously eagerly allocated curses pairs for every (fg, bg) combination of fish colors — O(N²) up front whether or not those combos ever appear on screen. Cross-color cells now route through `_lazy_color_pair`, allocating pair slots only for combos that actually render. Same machinery already used for bicolor lava.

## [1.8.0] - 2026-05-03

### Fixed

- **Ball radius not updated on terminal resize** (`lamp.py`) - `Lamp.resize()` now accepts an optional `new_ball_r` parameter and scales `self.ball_radius` proportionally. Without this, balls appeared too small on enlarged terminals or too large on shrunk ones. The resize handler in `app.py` passes the recomputed `ball_r` from `calculate_lamp_dims()`.
- **Campfire style missing flame squashing in metaball field** (`lamp.py`) - `compute_field()` and `compute_field_bicolor()` now check `self.style in ('fireplace', 'campfire')` instead of only `'fireplace'`, so campfire embers get the same asymmetric teardrop shaping (squashed bottom, long tail) and sine-wave "licking" motion as fireplace embers.
- **`--random` flag could produce mismatched campfire/xmas theme** (`app.py`) - The forced-theme override for `campfire` and `xmas` styles now applies regardless of `--random`. Previously `lavacli --random` could launch campfire fire logs against a teal koi pond background or green matrix colors behind flames.
- **`_resolve_fish_color` KeyError on unknown pattern name** (`themes.py`) - The method now uses `KOI_PATTERNS.get()` with a fallback to white (231) for unrecognized pattern names, preventing crashes if external code creates a `Fish` with an invalid pattern.

### Changed

- **Shared animation loop** (`app.py`) - The three near-identical main loops (`_run_lamp`, `_run_donut`, `_run_pond`) now delegate to a single `_run_animation()` function that handles the common frame timing, input dispatch, resize, HUD drawing, and refresh/sleep logic. Each mode provides callbacks for its specific update, draw, key handling, and HUD functions. This eliminates ~120 lines of duplicated code and makes adding new animation modes straightforward.
- **Profile interpolation uses binary search** (`lamp.py`) - `_interpolate_profile()` now uses `bisect` on pre-computed y-key arrays cached at module load time, replacing the O(n) linear scan. For the 25-point `BASE_PROFILE` this avoids up to 25 comparisons per call (called for every cell of cap/base rendering).

### Performance

- **Donut trig calls replaced with pre-computed lookup tables** (`donut.py`) - The nested rendering loops no longer call `math.sin`/`math.cos` ~28,000 times per frame. Instead, `Donut.__init__` builds sin/cos LUTs for the fixed theta (90 entries) and phi (315 entries) step sizes, reducing trig calls from 560,000/sec at 20fps to zero at runtime.
- **Perlin noise `math.floor` deduplicated** (`noise.py`) - `noise3()` previously called `math.floor()` six times (twice per coordinate). Now each coordinate's floor is computed once and reused for both the integer index and fractional part.

## [1.7.0] - 2026-04-23

### Added

- **`campfire` style** - A new dedicated fullscreen style (`--style campfire`) that always shows the layered pine forest silhouette scene with rolling hills, starry night sky, and warm campfire glow on the forest floor. Previously this required manually picking `--style fireplace --theme campfire`; it is now a first-class selectable style in both the CLI and the interactive menu.
- **`xmas` Christmas Fireplace style** - A new fullscreen style (`--style xmas`) rendering an indoor Christmas fireplace: red brick surround with a solid lintel, a thick wooden mantel shelf, two Christmas stockings (red with white cuffs) hanging from the mantel, a procedural hearth flame (black backdrop → dark red → red → orange → gold → white-hot center, tapering to a tip with time-based flicker), stone hearth at the base, and a dark warm-toned room with hardwood floor. Ember physics from the `fireplace` style rise on top of the flame layer for depth. Auto-selects the Christmas color palette (dark red → orange → gold embers) when launched without `--theme`.
- **`xmas` Christmas color theme** - Christmas ember palette auto-selected when launching `--style xmas` without an explicit `--theme`.

## [1.6.2] - 2026-04-23

### Changed

- **Donut color system redesigned** - Colors no longer cycle automatically. The donut now renders entirely in the active theme's palette and only changes color when the user explicitly presses `C` (cycles theme) or selects a theme via `--theme` from the CLI.
- **`--theme` flag now applies to donut mode** - Previously the flag was ignored for the donut style; it now sets the starting palette directly.
- **`B/V` keys cycle shade modes instead of sprinkle patterns** - The old sprinkle system (which picked colors from all 16 themes simultaneously) is replaced by 4 named shading modes within the single active theme:
  - **Smooth** — linear Lambertian shading across 5 palette levels (default)
  - **Glow** — same as Smooth with a specular rim highlight (theme's `rim` color) applied to the top 1/6 of luminance
  - **Bold** — high contrast; mid-tones are compressed toward the bright and dark extremes
  - **Dim** — softer appearance; all shades shifted one step toward the darker end of the palette
- **HUD updated** — `B/V:Sprinkles` label replaced with `B/V:Shade(Mode)` showing the active shade mode name; `C:Colors` retitled to `C:Theme` for clarity.
- **Menu donut preview respects theme selection** — Changing the THEME field in the menu now immediately updates the color of the live donut preview panel.

## [1.6.1] - 2026-04-23

### Fixed

- **Division by zero in Perlin noise** (`noise.py`) - `fbm3()` raised `ZeroDivisionError` when called with `octaves=0` because `max_val` was never incremented. Now returns `0.0` safely.
- **`KeyError` on invalid bi-color theme** (`themes.py`) - `set_secondary_theme()` guarded against `None` but not against unrecognised theme names, which raised `KeyError`. The early-return guard now also checks `theme_name not in THEMES`.
- **Frame-timing sleep burned only half the remaining budget** (`app.py`) - All three animation runners (`_run_lamp`, `_run_donut`, `_run_pond`) slept `remaining * 0.5` after a keypress instead of the full remaining frame time, causing the animation to run faster than the 20 fps target and waste CPU on rapid key input.

### Performance

- **Pond render buffer no longer re-allocated every frame** (`pond.py`) - The `[[None] * w for _ in range(ph)]` buffer inside `Pond.render()` was creating ~20 000 Python list objects per second at a typical terminal size. It is now cached on the instance and reset in-place each frame; only reallocated on terminal resize.
- **Donut z-buffer and color buffer no longer re-allocated every frame** (`donut.py`) - Same pattern: `z` and `col_buf` flat lists were recreated on every `Donut.render()` call. Both are now cached on the instance and reset via slice-assignment, with reallocation only on resize.
- **Lazy import moved to module level** (`pond.py`) - `from .themes import KOI_PATTERN_NAMES` was inside `_init_fish()` and `add_fish()`, causing an unnecessary module-cache lookup on every fish initialisation. Moved to module-level import.

## [1.6.0] - 2026-04-22

### Added
- **4 New Themes** - Cyberpunk (neon pink/cyan), Matrix (hacker greens), Oceanic (deep sea blues), and Campfire (cozy golden core through orange and red to dark ember glow at the edges, over a black night sky).
- **Procedural 3D Campfire Logs & Pine Forest** - The `fireplace` style now features a high-fidelity, procedurally generated log structure at the base. Includes 3D-shaded bark textures, concentric wood rings on log ends, glowing cracks/embers, and a scattered ash bed. The **Campfire theme** renders a layered **pine tree silhouette background** with rolling hills and a starry night sky.
- **Warm Firelight Glow on Forest Floor** - A radial amber/orange-brown glow emanates from the campfire center onto the forest floor, simulating warm light cast by the flames.
- **Licking Flame Animation** - Upgraded the fire animation with teardrop-shaped embers and sine-wave "licking" motion for the flame tails, creating an organic waving effect.
- **Sustained Flame Core** - Added a solid, swaying procedural flame pillar that emerges from the logs, providing a continuous core of fire.
- **Flame Shaping** - Revised ember temperature model forms a natural, triangular flame shape by cooling side embers faster than those in the center.

### Changed
- **Campfire palette corrected** - Flame colors now flow from dark maroon at the outer ember glow through red → orange → warm orange → golden yellow at the hottest center, matching how real fire looks (previously the gradient was inverted).
- **Wider campfire ember spawn** - Embers now spawn with an 8% Gaussian spread (was 4%), giving the fire a fuller, more natural base that matches the log width.
- **`ColorHelper` composite rendering** - Integrated procedural log and forest rendering into the half-block pipeline with true color compositing.


## [1.5.0] - 2026-04-13

### Added

- **Donut mode** - New 12th lamp style: a fullscreen spinning ASCII donut, ported from Andy Sloane's classic donut.c. The torus (R1=1, R2=2) rotates about two axes with perspective projection and Lambertian lighting, rasterized via the app's half-block pipeline so it composes with the existing theme/HUD/resize machinery. Sized so its projected diameter spans 70-85% of each terminal axis — a proper BIG SPINNING DONUT rather than a min-dim-capped miniature
- **Theme-cycling sprinkles** - Instead of donut.c's 12-character luminance ramp, each lit point on the torus picks its palette from `THEME_ORDER` and the Lambertian intensity picks the shade within that palette, so the donut is rendered entirely out of theme colors. A time offset rotates the selection every few frames, so the whole donut visibly cycles through all 12 themes as it spins
- **8 sprinkle patterns** - `B`/`V` during donut mode cycle the spatial component of the palette selection. Default `(0, 0)` is "solid" — whole donut shares one palette that shifts through every theme over time (clearest theme-cycling look). Other patterns layer in ring bands `(1, 3)`, tube stripes `(5, 1)`, broad wraps `(1, 7)`, diagonal confetti `(3, 5)`, chunky wedges `(0, 1)`, stacked hoops `(1, 0)`, and fine speckle `(7, 7)`
- **`ColorHelper.setup_donut_colors()`** - Pre-warms a curses color pair for every `(lava_color, liquid_bg)` and `(lava_color, lava_color)` combo across all 12 theme palettes (~120 pairs). Without this pre-allocation, `_lazy_color_pair` can silently fall back to the `(liquid, liquid)` pair mid-render when it runs out of slots — which was making sprinkles disappear
- **`ColorHelper.draw_colored_cell()`** - Generic half-block draw helper that accepts arbitrary ANSI-256 colors for the top and bottom cell halves, backed by the lazy pair cache. Used by the donut renderer so sprinkles from many themes can coexist on the same frame
- **Live donut preview in the menu** - Hovering "Donut" in the STYLE menu now renders a real miniature spinning donut in the preview panel, right next to the Koi Pond preview

### Changed

- **Sampling density** - Donut inner-loop steps match donut.c's originals (`θ=0.07`, `φ=0.02`), ~28k sample points per frame. Python sustains ~40 fps on a default terminal thanks to the flat buffer + integer palette index math
- **Width and height scale independently** - Earlier draft capped the donut on `min(w, ph)`, leaving tiny donuts on wide terminals. Now `scale_x = w * 0.58` and `scale_y = ph * 0.58` give a big ring on any aspect ratio

## [1.4.0] - 2026-04-12

### Added

- **Fireplace mode** - New 11th lamp style: a fullscreen crackling fireplace of rising embers. Reuses the metaball engine with inverted physics — embers spawn hot at the bottom, drift upward with flicker jitter and a slight updraft curl, cool monotonically as they rise, and recycle back to the bottom once they fade. Ember brightness is driven by `ball.temp` scaling the metaball field contribution, so fading embers naturally dim through the rim level before winking out. Pairs beautifully with the Sunset, Clear Red, and new Aurora themes
- **Aurora theme** - New 12th color theme: violet → magenta → green → cyan ribbons over a near-black night sky, with a purple halo glow and a dark metal base. Designed as the companion theme to Fireplace, but looks great on any fullscreen or glass lamp
- **Bi-color lava** (`--bicolor THEME_B` flag, `TINT` menu field) - A single lamp can now mix two palettes like the 90s red/blue Mathmos bi-color lamps. Half the blobs carry the primary theme's palette, half carry the secondary's. Color pairs for cross-palette combos are lazily allocated via a new `ColorHelper.set_secondary_theme` / `_lazy_color_pair` pathway, so only the (fg, bg) combos actually drawn consume curses pair slots. `B`/`V` during animation keeps the two palettes balanced
- **Blob trails** (`T` key) - Toggle a "slow-shutter" motion-blur effect during animation. Each cell that has lava is remembered in a per-lamp trail buffer for ~14 frames and then fades through lower lava levels down to the rim glow before disappearing — so every blob paints a soft comet-tail behind it. Works for both glass lamps and fullscreen styles (Freestyle, Fireplace). HUD shows `T:Trails*` while active
- **Menu `TINT` field** - New 6th menu row cycling through `Off` + all 12 themes. Selecting a tint flips the live preview panel into bi-color mode instantly. Number-key jumps now go `1`–`6` to cover the new field
- **`[A+B]` HUD marker** - Displayed in the bottom controls bar whenever bi-color is active so you can tell at a glance that two palettes are mixing

### Changed

- **Menu help line updated** to reflect the new `1-6 Jump` range
- **`Lamp` constructor** accepts an optional `bicolor=False` argument. When true, each ball is assigned `palette_id = i % 2` round-robin so the two palettes are evenly distributed from the start
- **`Ball.__slots__` gained `palette_id`** so every ball carries its palette identity without a dict lookup
- **Fireplace style overrides the user-picked flow** internally (forcing its own `fireplace` physics params) because ember behavior shouldn't depend on whether the user chose Zen or Chaotic

### Fixed

- **Resize during trails / bi-color no longer leaves stale buffer entries** - `Lamp.resize` now invalidates `trail_buffer` so the next frame reallocates at the new dimensions instead of indexing into a wrong-sized 2D list

## [1.3.0] - 2026-04-11

### Added

- **Live lamp preview panel in the menu** - When the terminal is at least 72 columns wide, a second bordered box appears next to the menu rendering a real miniature of the currently-selected configuration. Every selection change is reflected in real time — style, flow, theme, and even koi pond mode (complete with lily pads and fish) render live. Previously only theme cycling gave visual feedback
- **Inline theme palette swatch** - The THEME field now shows 5 colored blocks in the theme's lava palette next to the theme name, so you can compare palettes at a glance without committing
- **Option position indicator** - Every field now shows `(current/total)` next to its value (e.g. `◂ Classic ▸ (1/10)`) so you know how many options exist in each list
- **`R` key in the menu** - Randomizes all five fields at once. Great for "surprise me" discovery across 10 styles × 11 themes × 6 flows
- **`1`–`5` number-key jumps** - Press a digit to jump directly to STYLE, THEME, FLOW, COUNT, or SIZE without j/k-ing through the list
- **Wrap-around menu navigation** - `UP` from STYLE now wraps to the Launch button, and `DOWN` from Launch wraps back to STYLE. No more dead-ends
- **CLI flags for direct launch** - `lavacli --style koipond --theme koi_pond --flow swirl --count 3 --size G` skips the menu entirely and drops straight into the animation. All five fields are optional; omitted ones get sensible defaults. Huge for tmux startup scripts, shell aliases, and screensaver integration
- **`--random` flag** - Randomizes any unspecified fields before launch. Combines with explicit flags (e.g. `--random --style koipond` locks koi pond but randomizes the rest)
- **`--duration SECONDS` flag** - Run for N seconds then exit cleanly. Built for terminal screensaver use (`lavacli --random --duration 600` etc.)
- **`--version` flag** - Prints the installed version
- **`__version__` on the package** - `lavacli.__version__` now exposes the version string in code

### Changed

- **Menu help line rewritten** to reflect the new keys: `↑↓←→ Nav  1-5 Jump  R Rand  Enter  Q Quit`
- **`Pond.render()` now accepts optional `x_off` / `y_off` offsets** so the pond preview can render into an inset region of the menu screen. Default behavior (no offsets) is unchanged
- **`app.run()` now accepts an optional `argv` argument** for argparse testing and programmatic invocation; existing `run()` with no args still works as a setuptools `console_scripts` entry point

### Fixed

- **ColorHelper pond pairs not allocated in the menu** - The koi pond preview panel crashed on first draw because `ColorHelper.setup()` doesn't allocate fish/water color pairs (those normally come from `setup_pond_colors()` inside `_run_pond`). The menu now calls `setup_pond_colors()` during init and refreshes it after every theme change, so the preview can render koi pond without `AttributeError: '_water_pair'`

## [1.2.1] - 2026-04-09

### Fixed

- **README on PyPI** - The 1.2.0 wheel was built before the install section was updated for the `pylavalamp` distribution name, so the live PyPI page contradicted itself ("LavaCLI isn't published to PyPI — install it from a local clone" while being read on the PyPI page). 1.2.1 republishes the package with the correct README: `pipx install pylavalamp`, the real GitHub repo URL, and accurate Python version requirement (3.8+, matching `requires-python`)
- **Stale Python version in README requirements** - was `Python 3.6+`, now matches `pyproject.toml`'s `requires-python = ">=3.8"`
- **Duplicate "Koi Pond Mode" feature bullet** in README — was listed twice, now consolidated into one richer line

### Added

- **PyPI / Python version / License badges** at the top of the README, reading live data from `https://pypi.org/project/pylavalamp/`
- **"Koi Pond" subsection in README "How It Works"** explaining 14-segment fish physics and lily pad rasterization
- **"Solid Base/Cap" README section** now mentions the rocket's serrated three-fin profile and chrome highlight stripe (was still describing the old torpedo rocket)

## [1.2.0] - 2026-04-09

### Added

- **Lily pads in Koi Pond mode** - 6-10 sage-green elliptical lily pads are scattered across the pond at random non-overlapping positions, each with a characteristic V-notch and 3-tone shading (rim/fill/shadow) for a watercolor look. Fish swim *over* the pads
- **Koi Pond theme** - New 11th color theme with teal water, white-orange koi-friendly lava palette, and sage lily pads — matches the watercolor reference aesthetic
- **Lily pad palette in every theme** - All themes now include `lily_pad` / `lily_pad_dark` / `lily_pad_rim` slots so pads stay sage-green regardless of which theme is active
- **`LilyPad` class in `pond.py`** with Poisson-ish placement that scales count and size to pond dimensions, regenerated automatically on terminal resize

### Changed

- **Rocket lamp redesign** - Cylindrical glass column (was torpedo/bullet bulge), sharper and longer pointed nose cone, three distinct swept-back fins suggested by serrated profile valleys, and chrome highlight stripe down the center of the cap and fin base for a polished metal look. Glass column is now framed by chrome columns instead of dark glass border (rocket only). Inspired by the Mathmos rocket reference image
- **Kohaku/Sanke fish bias** - Pond fish init weights kohaku (white with orange) and sanke higher so the default pond reads as a classic koi pond at a glance

### Fixed

- `Pond._fill_width` and `_fill_fin` now correctly overwrite lily pad cells (previously would have raised IndexError when a fish swam over a pad)

## [1.1.0] - 2026-04-07

### Added

- **Koi Pond mode** - New fullscreen style with animated, colorized koi fish swimming around the terminal
- **6 koi color varieties** - Kohaku (orange/white), Sanke (red/white/black), Showa (red/white on black), Tancho (red crown/white), Ogon (solid gold), Asagi (blue-gray/orange)
- **Skeletal fish physics** - 14-segment body chain with constraint-based movement and sinusoidal swimming undulation, inspired by [cpond](https://github.com/ayuzur/cpond)
- **Fish body shape** - Pointed snout, bulging belly, pectoral fins, narrow caudal peduncle, and fanning tail fin
- **Pond color system** - Fish-on-water color pair allocation with per-body-part coloring (head, body patches, fins, tail)
- New `pond.py` module with `Segment`, `Fish`, and `Pond` classes
- `B`/`V` keys add/remove fish in Koi Pond mode
- All 10 themes work with Koi Pond (water color adapts to theme liquid)

## [1.0.0] - 2026-04-07

### Added

- **Global install via pipx** - `pipx install lavacli` makes the `lavacli` command available from anywhere in the terminal
- **`pyproject.toml`** - Standard Python packaging with `console_scripts` entry point

## [0.3.0] - 2026-04-07

### Added

- **Rocket style** - Mathmos Telstar-inspired rocket ship lava lamp with pointed nose cone and swept-back fin base
- **Cylinder style** - Vintage straight-tube lava lamp with flat disc cap and simple cone base
- **Pear style** - Retro bulbous shape with narrow neck and wide belly
- **Freestyle mode** - Fullscreen lava fills the entire terminal with no lamp frame
- **Liquid flow type** - Pure-Python 3D Perlin noise with fractal Brownian motion for smooth organic flowing patterns
- **Rim/edge glow effect** - Dual-threshold metaball rendering creates a glowing halo around each lava blob
- **Groovy animated menu** - Lava background animation, rotating groovy taglines, decorative border, live theme preview
- **3 new themes** - Blue Purple, Clear Red, Clear Orange (inspired by classic Lava Library color codes)
- **Return to menu** - Press `M` during animation to go back to the menu
- **Toggle HUD** - Press `H` to show/hide the bottom controls bar for a clean view
- Pure-Python `noise.py` module with Perlin noise and FBM (no external dependencies)

### Changed

- **10 color themes** (was 7) - all renamed to clean names, inspired by 1992-2004 Lava Library catalog
- **Dark bases** - All themes now use dark gray/black bases matching classic lava lamp aesthetics
- **Dark glass frame outline** - Glass border uses dark contrasting color for pixel-art style definition
- **Improved base profile** - Proper hourglass shape matching the real Lava Original silver base
- **Improved cap profile** - Wide cylindrical collar band instead of tiny dome
- **3-tone metallic shading** - Base and cap use highlight/mid/shadow for richer metallic appearance
- **Fixed cap rendering bug** - Cap was invisible due to coordinate system mismatch (absolute vs local)
- **Wider glass top** - Classic shape now starts at 0.36 width (was 0.22) matching real lamp proportions
- **Better proportions** - Glass ~57%, Base ~34%, Cap ~8% of total height (was ~73%/22%/5%)
- **More blobs** - Default ball counts increased for more impressive display
- **Faster animation** - ~20fps (was ~14fps) for smoother lava flow
- **9 styles** (was 5) - added Cylinder, Pear, Rocket, and Freestyle
- **6 flow types** (was 5) - added Liquid (Perlin noise)
- Menu now shows only selected option per field (no overflow)

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
