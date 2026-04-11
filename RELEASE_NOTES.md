# Release Notes

## Version 0.13.0 - Routing Modularization, SQLite Fixes, and Scaffold Expansion

Release date: 2026-04-10

This release focuses on project scaffolding quality and day-two developer workflow improvements. It resolves database configuration issues, modernizes generated web output, and adds extensible scaffolding commands for existing projects.

## Highlights

### 1. SQLite setup now uses Flask instance storage
When SQLite is selected during project creation, generated Flask apps now configure SQLAlchemy to use a database file under `app.instance_path`.

What changed:
- Instance folder is created automatically.
- SQLite database path is generated with `os.path.join(app.instance_path, "<app>.db")`.
- Path is normalized before building `SQLALCHEMY_DATABASE_URI`.

Why this matters:
- Matches Flask-recommended instance-based storage.
- Prevents accidental URI mismatch when SQLite is selected.
- Avoids committing local DB files into package code paths.

### 2. `amen run` now targets `app.py`
The run command now executes `app.py` for generated projects.

What changed:
- Runtime entry file changed from `run.py` to `app.py`.
- User facing next step messaging now points to `python app.py`.
- Documentation references updated to align with current behavior.

Why this matters:
- Aligns command behavior with generated scaffold files.
- Removes confusion around outdated runner filenames.

### 3. Endpoint scaffolding is now modular
Generated endpoint logic is no longer concentrated in a single module.

Flask scaffold now creates:
- `api/home.py`
- `api/health.py`
- `api/protected.py`
- `api/__init__.py` to import route modules

FastAPI scaffold now creates:
- `api/root.py`
- `api/health.py`
- `api/protected.py`
- `api/endpoints.py` as router aggregator

Why this matters:
- Cleaner organization as routes grow.
- Easier file ownership and feature focused edits.
- Better extension path for new endpoints.

### 4. New `add` command for incremental scaffolding
A new command supports adding project components after initial creation.

Supported syntax:
```bash
am add endpoint <name>
am add util <name>
am add view <name>
```

Command behavior:
- Accepts only `endpoint`, `util`, or `view`.
- Normalizes names (`-` and spaces become `_`) and validates identifier format.
- Uses project framework from `.amen_config`.

Generated artifacts:
- `endpoint`: framework-specific route module.
- `util`: `utils/<name>.py` helper module.
- `view`: endpoint module + `templates/<name>.html` page.

Framework integration:
- Flask: route module is auto-registered in package `__init__.py` import line.
- FastAPI: new router module is auto-included in `api/endpoints.py`.

### 5. Default web index page redesign
The generated web app landing page was refreshed with a more modern, production-style visual baseline.

Included improvements:
- Better hierarchy and typography.
- Updated layout with responsive sections and feature cards.
- More polished visual treatment for first-run UX.

## Documentation updates
- Project structure examples updated to reflect endpoint module separation.
- Runner references updated from `run.py` to `app.py`.
- Flask/FastAPI endpoint architecture notes revised.

## Version updates
Updated to `0.13.0` in:
- `pyproject.toml`
- `setup.py`

## Notes
- Existing projects with older route layouts continue to work, but newly generated projects now use modular route files.
- Existing projects can adopt the new approach incrementally using `am add`.

## Quick verification checklist
1. Create a Flask app with SQLite and confirm URI points to the instance DB.
2. Run `am run <app>` and verify `app.py` is executed.
3. Generate a new project and confirm separate endpoint modules are present.
4. Run `am add endpoint profile`, `am add util email`, and `am add view dashboard` and verify files are created and registered.

## Thank you
Thanks to everyone providing project structure and workflow feedback that shaped this release.
