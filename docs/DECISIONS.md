# Review decisions

## 2026-10-19: Replace the illustrated welcome with a command reference

Status: accepted for the user's explicit design correction.

Use a compact Laravel-inspired welcome panel, warm neutrals, red accents,
documentation links and a restrained command grid. Remove the right-side SVG
illustration and its preview styles/tokens. Keep the AMEN version visible beside
the logo and in project metadata/footer. Replace the former three tabs with
all thirteen CLI commands, three `add` examples and global help: sixteen examples
with plain descriptions, correct project arguments and copy buttons.

Add progressive search across titles, syntax and descriptions. Keep all commands
visible without JavaScript. Generate the monitor port from framework metadata
and choose port 5051 for the documentation example to avoid the Flask app port.
Examples only copy text; they never execute commands through the page.
Preserve working theme/clipboard/health behaviors, local assets, API roots and
escaping. Retain 0.14.0 while revising this uncommitted, unpublished release.

This supersedes the initial illustrated visual direction and command-tab design
below. Regression checks verify the examples with Click without invoking them.

## 2026-10-19: Share an offline welcome UI and prepare 0.14.0

Status: accepted for the user's welcome-page redesign and version-update request.

Use one source HTML/CSS/JavaScript asset set for Flask and FastAPI webapps.
TemplateManager provides app/framework/database/version metadata and copies the
assets; a small renderer escapes substitutions before the framework's Jinja
render. Existing API roots remain JSON and existing projects are not rewritten.
Removing the older common CSS/JS output prevents later generation from replacing
the welcome styles. Asset writes accept bytes for the bundled font.

Serve tokens, icons, scripts and Instrument Sans locally. Preserve the font's
SIL OFL license in both the CLI package and generated projects. Plain JavaScript
keeps the generated application free of frontend build dependencies.

Show health only from a real successful `/health` response, with manual refresh,
JSON inspection, error/retry handling and an eight-second timeout. Theme choice,
keyboard command tabs and clipboard feedback provide useful interactions without
simulated dashboard metrics. Respect reduced motion and keep static content
readable when JavaScript is unavailable.

Select **0.14.0**: the new welcome experience is a feature addition, alongside
the earlier database, rendering, collision, authentication and command-failure
repairs. Update pyproject/setup and release documentation together; confirm the
installed CLI, generated pages, sdist and wheel agree. Preparation does not
publish a package or create a release tag.

## 2026-10-19: Document improvements before implementing them

Status: accepted for this review.

The requested deliverable is a feature recommendation and an audit of existing
features. This change documents evidence and a proposed implementation order.
Runtime fixes and new commands require a subsequent implementation task.
Proposed product choices in the roadmap are recommendations, not implemented
features or approved architectural changes.

## Proposed: prioritize resource generation after foundation repairs

Status: recommendation; implementation not started.

Extend the existing `add` workflow to generate a complete resource rather than
an empty endpoint. Start with Flask/SQLite and require working migrations,
validated names, collision handling, and behavioral tests. FastAPI/MySQL follow
their database integration fixes. A read-only `doctor` command and unattended
creation are smaller supporting capabilities.

## Proposed: preserve legacy projects when enriching metadata

Status: recommendation; format not selected.

Current `.amen_config` stores only a framework name. New commands need the
package name, application type, database, entry point, environment, port, Python
requirement, and scaffold version. Introduce versioned metadata with a legacy
reader; do not silently reinterpret or overwrite existing projects. Select the
format during implementation, with migration and compatibility tests.

## 2026-10-19: Implement the three selected repairs

Status: accepted for the user's request to fix three issues including DB scaffolding.

The selected scope is F01 (FastAPI rendering), F02 (database scaffolding), and
F06 (preserving existing files during incremental scaffolding). The new resource
command and other review findings remain future work.

Database templates live in `amen/templates/database.py`. Database-free projects
omit all database code/dependencies. Flask uses Flask-SQLAlchemy/Flask-Migrate;
FastAPI uses SQLAlchemy 2 sessions and Alembic. Both register generated models,
read `DATABASE_URL` before database initialization, resolve relative SQLite paths
against the project root, and compute UTC creation timestamps per inserted row.
PyMySQL is the sole generated MySQL driver. One dependency selector supplies both
creation installs and generated requirements. Existing generated projects are
left intact; these changes affect future scaffolds.

Incremental generation refuses collisions instead of adding force/preview flags.
New files are created exclusively and removed on failure; existing registration
files are replaced atomically to preserve their contents on failed writes. Existing
name validation/registration detection and migration command semantics remain
outside this repair except for required backend selection and failure reporting.

## 2026-10-19: Observable command failures and Flask authentication

Status: accepted for the user's follow-up repair request (F08 and F05).

Expected command failures use Click errors instead of printed messages followed
by normal returns. Child tool failures preserve positive exit codes; signal
terminations map to `128 + signal`. Audit findings exit 1 after emitting the
report; clean audits exit 0. Optional cache failures remain recoverable when the
actual installation succeeds. Ctrl+C remains a normal stop for monitoring.

`AmenCLI.create_app(*, interactive=True)` now returns a `Path` only after setup,
installation, scaffolding, and metadata writing succeed. Invalid input raises
`click.BadParameter`; noninteractive existing targets raise `ProjectExistsError`;
setup errors raise Click exceptions. Web requests call with `interactive=False`
and translate these to 400/409/500 respectively. Successful responses preserve
status/message and add canonical name/path. No metadata format migration occurs.

The Flask token template validates exactly two whitespace-separated header parts
and a case-insensitive Bearer scheme before decoding. Only PyJWT token validation
exceptions become 401; unrelated decoder/configuration/handler failures continue
to surface as application errors. Existing generated applications are not edited.

Web monitoring runs its server in the foreground so startup failures reach the
command and stopping it cannot fall through into terminal monitoring. Process
selection, CPU sampling, dashboard port selection/debug defaults, and browser
refresh remain separate pending work.
