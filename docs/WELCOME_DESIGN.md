# Welcome page design and behavior

Project: AMEN CLI 0.14.0. Framework: generated Flask/FastAPI webapps.
Styling: local CSS; interactions: plain JavaScript; SVG is limited to small
functional icons. Scope: six source files in `amen/templates/`, plus font/license.
Mode: apply. Skills: Sites local QA and polish (typography, color, spacing,
depth, motion, responsive). This revision implements the user's request for a
Laravel-like design, visible AMEN version, no illustration, and command descriptions.

## 10x Polish Report

The page now uses a compact welcome panel, understated borders, warm neutral
surfaces and a red accent. The visual reference is Laravel's
[official welcome template](https://github.com/laravel/laravel/blob/12.x/resources/views/welcome.blade.php).
The former split hero, decorative sculpture and command tabs are removed.

| Area | Finding | Applied change | Risk |
| --- | --- | --- | --- |
| Typography | Oversized marketing copy distracted from project information | A 32–48px welcome heading and readable command titles/descriptions; visible version badge | Low |
| Color | Green styling did not match the requested Laravel direction | Warm white/charcoal surfaces, a red accent and complete light/dark roles | Low |
| Spacing | The illustrated hero occupied useful space | One compact welcome panel followed by an aligned command reference | Low |
| Depth | Decorative preview was too prominent | Thin borders and a quiet shadow on the welcome panel; flat command rows | Low |
| Motion | Useful interaction feedback should survive the redesign | Preserve copy/health/theme feedback and reduced-motion support; remove decorative entrance effects | Low |
| Responsive | Commands need to stay readable across widths | One-column mobile/two-column desktop grid, wrapping code and a full-width mobile search | Low |

Six grouped findings addressed in one aligned redesign. The single primary
button links directly to “AMEN commands.” The version is visible in the header,
project metadata and footer. The illustration and associated art tokens are gone.

Preview: [light theme](images/welcome-light.png), [dark theme](images/welcome-dark.png).
Screenshots show a disposable Flask/no-database app named `northstar`.

## Consolidated implementation

| Source | Responsibility |
| --- | --- |
| [welcome_page.py](../amen/templates/welcome_page.py) | Escape app/framework/database/default-port/version values and return local assets |
| [manager.py](../amen/templates/manager.py) | Generate shared webapp HTML/assets for both frameworks |
| [index.html](../amen/templates/welcome/index.html) | Welcome, visible version, docs, command examples/descriptions, health disclosure |
| [tokens.css](../amen/templates/welcome/tokens.css) | Font, palette, semantic roles, type, spacing, elevation, motion |
| [welcome.css](../amen/templates/welcome/welcome.css) | Layout, components, focus states, themes and reduced motion |
| [welcome.js](../amen/templates/welcome/welcome.js) | Search, clipboard feedback, theme preferences and health checks |

Generated paths are `templates/index.html`, `static/css/welcome-tokens.css`,
`static/css/style.css`, `static/js/app.js`, and `static/fonts/` in the app package.
The common-file generator does not overwrite these assets. API-only roots remain
JSON. Changes apply to new projects; existing project pages are preserved.

## Tokens generated

The single token source is [tokens.css](../amen/templates/welcome/tokens.css),
packaged with the template and emitted as `static/css/welcome-tokens.css`.
No root `10x.config.json` is present.

- Typography: local Instrument Sans, system monospace, shared 12/14/16/20/25/31px
  scale, fluid 32–48px heading and 14px version badge.
- Color: red 50–900, warm neutral 50–950, semantic success/error/idle colors,
  and background/card/raised/text/border/button/code roles in both themes.
- Spacing: 4/8/12/16/20/24/32/40/48/64/80px; small consistent border radii.
- Depth: a two-layer welcome shadow and separate toast elevation.
- Motion: 120/180ms controls, 900ms health progress, shared easing. Only transform
  and opacity animate; reduced motion removes repetition/travel.
- Responsive: mobile base, 640px resource columns, 768px command columns.

Instrument Sans Latin variable WOFF2 is bundled from
`@fontsource-variable/instrument-sans` 5.3.0, unchanged, under its
[SIL Open Font License](../amen/templates/welcome/fonts/OFL.txt). Both font and
license are copied into generated apps; non-Latin text uses system fallbacks.

## Command reference

All thirteen CLI commands are represented. There are sixteen copyable examples
because `add` has three variants and global `--help` has its own entry.

| Example | Description |
| --- | --- |
| `amen run <app>` | Start the project's development server |
| `amen create` | Open the new-project setup wizard |
| `amen add <app> endpoint hello` | Add and register an API endpoint |
| `amen add <app> view about` | Add a template and view route |
| `amen add <app> util helpers` | Create a reusable utility module |
| `amen test <app>` | Run project pytest/coverage |
| `amen install <app> requests` | Install a package into the project environment |
| `amen migrate <app>` | Generate/apply migrations; requires a database-enabled project |
| `amen audit <app>` | Scan Python code with Bandit |
| `amen monitor <app> --port <port>` | Monitor process/resource usage on the server's port |
| `amen config <app>` | Open `.env` in the Ring desktop editor |
| `amen web` | Start browser-based project creation on port 5050 |
| `amen docs --port 5051` | Start offline docs on a port separate from the app |
| `amen about` | Display installed CLI version and project information |
| `amen update` | Check for a newer CLI release and follow the update prompt |
| `amen --help` | List commands; use command-specific `--help` for options |

Rendered examples use the actual app name. Monitor defaults come from framework
metadata (Flask 5000, FastAPI 8000); users can match `--port` to their server.
Project commands run from the parent directory. The `am` alias also works.
Descriptions state requirements without claiming to resolve remaining CLI issues.
Copying an example does not execute it.

Key source locations: version badge at `welcome/index.html:32`, command grid at
`welcome/index.html:79`, search at `welcome/welcome.js:41`, typography/color/
spacing/depth in `welcome/tokens.css:32` / `:11` / `:42` / `:56`, and responsive
rules at `welcome/welcome.css:109`, all relative to `amen/templates/`.

## Interaction contracts

- Search matches command titles, syntax and descriptions without regard to case;
  empty queries restore all examples. A polite status reports the visible count,
  and no results shows a useful empty state. Query text uses `textContent`.
  All examples remain available without JavaScript; search is only revealed when
  its behavior is initialized.
- Copy uses the Clipboard API and selection/copy fallback. Success gets visible
  and screen-reader feedback; denied access leaves text selected for manual copy.
- Theme starts from a saved valid preference or the operating system. Storage
  denial leaves controls usable; system changes are followed without a saved choice.
- Health runs once on load and on request, fetching same-origin `/health` without
  caching. Successful `status: healthy` JSON is required to show healthy state.
  Status, measured duration and JSON are inspectable. Connection/HTTP/JSON/body
  errors and eight-second timeouts clear stale data and allow retry. Displayed
  JSON is capped at 12,000 characters; nothing injects response/query HTML.
- Skip navigation, visible focus rings, labeled controls, polite status updates,
  reduced motion and 44px copy/theme/health buttons support keyboard and touch.
  Without JavaScript, health remains explicitly unchecked.

## Validation and limits

Maintained integration tests exercise Flask/FastAPI × none/SQLite/MySQL. They
verify metadata/version, command completeness/descriptions, valid Click syntax
without invoking commands, project arguments/default ports, copying/search
wiring, absence of the illustration, local assets/font/license, API JSON and
HTML/Jinja escaping. MySQL checks do not connect to a live server.

See [PROGRESS.md](PROGRESS.md) for measured test/browser/build results. Browser
QA uses temporary Playwright/axe tooling outside the repository, adding no
frontend build or browser dependency to generated apps. Accessibility scans
supplement visual and keyboard checks; they are not a full conformance audit.
Native Safari/Firefox, older browsers, macOS/Windows and deployment subpaths
remain unverified. Version remains 0.14.0 for this prepared, unpublished release.
