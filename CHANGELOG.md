# Changelog

All notable changes to this project will be documented in this file.

## [0.14.0] - 2026-10-19

### Added

- A Laravel-inspired welcome page for generated Flask and FastAPI webapps, with
  light/dark themes, a prominent AMEN version badge, project details, searchable
  commands with descriptions and copy controls, and real health/JSON inspection.
  The layout focuses on useful content without a decorative illustration.
- Local welcome-page styles, scripts, and a licensed Instrument Sans font that
  work without runtime CDN services.

### Changed

- Bump package metadata to `0.14.0` for the interactive welcome page and the
  accumulated database, scaffolding, authentication, and command-handling updates.
- Failed commands now return meaningful nonzero statuses. Automation that relied
  on a successful status after an error must handle these failures explicitly.
- New welcome templates and scaffold fixes apply to newly generated projects;
  existing generated applications are not rewritten.

### Fixed

- Generate database setup per framework and database choice. No-database apps
  omit database dependencies; Flask loads models into migration metadata; FastAPI
  receives SQLAlchemy sessions and an Alembic migration environment.
- Use the selected database dependencies consistently for installation and
  generated requirements, honor `DATABASE_URL`, use PyMySQL for MySQL, and compute
  model timestamps for each inserted row without requiring `pytz`.
- Dispatch `amen migrate` to Flask-Migrate or Alembic and report unsupported
  no-database projects and migration failures with nonzero exit status.
- Render generated FastAPI homepages and added views with explicit template
  response arguments compatible with FastAPI 0.108.0 and later.
- Refuse existing endpoint, utility, and template paths in `amen add` before
  writing files, and remove newly created output if a write or registration fails.
- Return nonzero on command validation, setup, editor, server startup, and tool
  failures; preserve failed application/test/install/migration subprocess exit
  codes and include captured diagnostics. Run application servers without a shell.
- Return a project path only after successful creation. Web requests return
  validation/conflict/setup HTTP errors, avoid terminal overwrite prompts, and
  report the actual normalized project name and path on success.
- Parse Flask bearer headers safely and return 401 for malformed or invalid
  credentials, while preserving unrelated application errors.
- Return Bandit findings/tool exit statuses, normalize severity aliases, exclude
  the project environment, and preserve machine-readable report output.
- Validate monitor refresh/port values and run the web monitor in the foreground
  so startup failures reach the CLI and stopping it does not start another monitor.

### Tests

- Add generated-app, SQLite persistence/migration, dependency-selection,
  FastAPI-rendering, and incremental-scaffold collision regression coverage.
- Add command failure/success, Flask authentication, and web-creation HTTP/error
  contract regression coverage.
- Check generated welcome HTML and local CSS/JavaScript delivery across both
  frameworks and database selections, while preserving API-only JSON responses.

## [0.13.1] - 2026-04-11

### Changed
- Project creation now installs framework dependencies from local cache first after virtual environment setup.
- If required packages are not available in cache, installation now falls back to online package installation.

### Fixed
- Fixed cache detection/install behavior so package creation no longer fails due to strict wheel filename matching.

### Versioning
- Bumped package version from `0.13.0` to `0.13.1` in project metadata.

## [0.13.0] - 2026-04-10

### Added
- New `add` CLI command to scaffold project parts in existing apps:
  - `am add endpoint <name>` creates a new endpoint module.
  - `am add util <name>` creates a utility module in `utils/`.
  - `am add view <name>` creates an endpoint plus an HTML template for server-rendered pages.
- Framework-aware endpoint scaffolding for both Flask and FastAPI.

### Changed
- `run` command now executes `app.py` instead of `run.py`.
- Flask SQLite scaffolding now uses the Flask instance folder for the database file.
- Scaffolded endpoints are now split into multiple modules instead of a single `endpoints.py` file.
- Default generated index page has been redesigned with a modern landing-page style inspired by current starter pages.
- Documentation updated to reflect new app runner and endpoint module structure.

### Fixed
- Corrected Flask SQLite database URI generation so `sqlite3` selection no longer produces a MySQL URI.

### Versioning
- Bumped package version from `0.12.0` to `0.13.0` in project metadata.
