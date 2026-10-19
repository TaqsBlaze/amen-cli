# AMEN CLI implementation context

Updated: 2026-10-19. Reviewed baseline: `f447571` (0.13.1).

AMEN is a Click-based Python CLI. `amen/cli.py` implements commands,
`amen/templates/manager.py` generates applications, and `amen/frameworks.py`
defines base framework packages and selected database dependencies. The web
creator and monitor are Flask applications. `.amen_config` still stores a
framework name; no metadata migration is introduced.

## Current repair scope

The first repair implemented F01 FastAPI HTML rendering, F02 database scaffolding,
and F06 collision protection for `amen add`. The follow-up implements F08 command/
web failures and F05 malformed Flask authentication, with related audit and
monitor failure handling. Other findings/proposed commands remain on the roadmap.

Primary ownership: template manager, new database templates, framework dependency
selection, scaffold integration tests, and documentation. Supporting implementer:
CLI creation/install wiring, migration dispatch, incremental generation, and CLI
regression tests. Both coordinate interfaces through these documents/messages.
The original README/review documentation changes are preserved.

## Current contracts

- `get_framework_packages(framework, database='sqlite3')` provides the same list
  for creation installs and generated requirements; no-DB projects omit DB packages.
- Database templates are in `amen/templates/database.py`. Both frameworks export
  the generated `Users` model through their models package. Flask loads it before
  migration setup; FastAPI registers it with SQLAlchemy's shared `Base`.
- Generated DB configuration reads project `.env` and external `DATABASE_URL`;
  relative SQLite paths are rooted at the project, defaulting to `instance/`.
  Model timestamps use a per-row UTC callable without `pytz`.
- FastAPI exports `Base`, `engine`, `SessionLocal`, and `get_db`, and includes
  Alembic configuration/scripts. No-database projects omit models/database files.
- `amen migrate` uses the project interpreter and the selected framework backend,
  rejects no-DB projects, and returns errors on failed migration subprocesses.
- `amen add` rejects file/directory/symlink collisions before writing. It creates
  files exclusively, preserves existing utility initializer content, and removes
  newly created output on failed writes/registration. No replacement flags added.
- Initial and added FastAPI views use explicit template-response arguments;
  generated dependencies require FastAPI >=0.108.0.

## Remaining known issues and validation limits

Repository scaffold tests now exercise generated app behavior and SQLite
migrations. Generated projects' own tests are still placeholders. The minimal
`create_project()` helper remains separate from actual CLI creation. Name and
registration substring checks, monitoring process/sampling/polling behavior,
headless editor support, updater installation strategy/version comparison, and
broader configuration issues remain pending.

See [PROGRESS.md](PROGRESS.md) for measured validation and its limits,
[ROADMAP.md](ROADMAP.md) for the historical findings/current status, and
[TODO.md](TODO.md) for pending work. No live MySQL or native macOS/Windows
integration is claimed by the SQLite and import checks.

## Follow-up contracts

- Expected failures use Click exceptions. Run/test/install/migrate child failures
  preserve exit codes; signal exits use `128 + signal`. Cache misses are nonfatal only
  when fallback installation succeeds. Server launching uses an argument list.
- `AmenCLI.create_app(*, interactive=True)` returns a project `Path` on completed
  setup, raises `BadParameter` for invalid input, `ProjectExistsError` for
  noninteractive conflicts, and Click errors for setup failures/cancellation.
- Web creator routes are registered once. HTTP 400 covers invalid input, 409 target
  conflicts, 500 failed setup, and 200 genuine creation with actual name/path. It
  calls creation noninteractively and never prompts to overwrite a target.
- Flask token templates validate the bearer scheme and header structure before
  decoding. Missing/malformed/invalid/expired credentials return 401; valid tokens
  retain 200 responses; unrelated decoder/handler failures are not hidden.
- Audit invokes the CLI's Bandit module with normalized severities and environment
  exclusion. It emits raw reports, returns 0 clean/1 findings/tool status on errors.
- Monitor refresh/port input is validated; web startup runs in the foreground so
  failures propagate. Monitoring stops normally on Ctrl+C.

Follow-up ownership: primary handled CLI failure handling, monitor startup,
regression tests and documentation; supporting implementer handled the Flask
header template, web creation, and auth/web tests. Prior repairs are preserved.

## Premium welcome page and 0.14.0 release

The user authorized replacing the generated default webapp HTML with a premium,
interactive UI and bumping the version for all accumulated updates. This is local
CLI source/template work; no hosted Site or package publication is requested.
Apply-mode UI skills use the generator sources as scope, not generated fixtures.

Primary owns welcome template/assets, generator integration, browser QA, design
notes and shared docs. Supporting agent owns version metadata, changelog/release
notes, and new generated-welcome integration tests. Target version is 0.14.0.
The shared welcome asset contract was coordinated before edits. Prior bug fixes
and their regression tests are preserved.

- `get_welcome_files(app_name, framework, database, version)` returns a mapping
  of relative generated paths to UTF-8 text or binary font bytes. It escapes
  metadata in one pass, including braces that must not become Jinja syntax.
- `TemplateManager` writes shared local welcome assets only for webapps and
  supports binary files. Common-file generation no longer replaces these styles
  or scripts. API-only root responses stay JSON.
- `amen/templates/welcome/` owns the HTML, design tokens, CSS, JavaScript,
  Instrument Sans WOFF2, and its SIL OFL license. No runtime CDN is required.
- Themes, a searchable command reference, clipboard feedback and genuine same-origin
  health checks progressively enhance a readable static page. Health checks
  clear stale responses, distinguish failures, and time out after eight seconds.
- Both packaging metadata files declare 0.14.0. `amen.__version__` reads installed
  distribution metadata; reinstall the editable package after changing version
  fields to validate generated page and CLI version output.
- Newly generated webapps receive the redesign. No automatic existing-project
  rewrite or package publication is part of this change.

See [WELCOME_DESIGN.md](WELCOME_DESIGN.md) for the implementation breakdown,
token location, interaction contracts, screenshots and validation limits.

## Welcome revision: Laravel-inspired command reference

The user requested replacing the illustrated layout with a Laravel-like page,
a clearly visible AMEN version, no right-hand illustration, and AMEN command
descriptions. Primary owns the page/tokens/styles/search and docs/screenshots;
supporting agent owns only welcome regression tests and command syntax review.
Version stays 0.14.0 while refining the prepared release. The default port is
now a framework-derived escaped template value used by monitor examples.
All command examples remain visible without JavaScript; enhanced search filters
by title, command and description. Theme, copy, and health behavior are retained.
The version appears in a header badge, project metadata and footer.

## Release execution

The user explicitly authorized a detailed commit, push and GitHub release for
0.14.0. Release publication triggers the existing python-publish workflow, which
builds distributions and attempts PyPI publication. No new workflow is needed.
Use annotated tag v0.14.0 at the committed change set. Authentication and remote
publication state are checked separately from the completed local validations.
