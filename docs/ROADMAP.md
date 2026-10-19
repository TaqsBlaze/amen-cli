# AMEN CLI feature review and roadmap

Reviewed on **2026-10-19**, against **0.13.1 / `f447571`**.

The original findings below describe review baseline `f447571`; their source
links are pinned to that commit. The proposed new commands remain unimplemented.
Follow-up implementations address the following selected findings:

| Finding | Current status |
| --- | --- |
| F01: FastAPI HTML rendering | Fixed for generated homepages and added views |
| F02: Database scaffolding | Fixed framework-specific setup, model discovery, sessions, timestamps, selected dependencies, and migration dispatch; real SQLite migrations tested |
| F06: Incremental scaffolding overwrites | Fixed collision preflight, exclusive creation, and rollback of new output on write/registration errors |
| F05: Malformed Flask authentication | Fixed bearer parsing and invalid/expired token responses across generated Flask variants |
| F08: Command/web results | Fixed nonzero failures, child exit-code propagation, shared creation outcomes, and web HTTP validation/conflict/setup errors |

Preview/replacement flags, redesigned migration subcommands, and live MySQL
integration remain follow-up work. Existing generated projects are not rewritten.
F09 audit severity/status/environment exclusion/report-output repairs are also
included with command handling; remaining formatter integration checks are
tracked separately. F12 refresh validation and monitor startup/error propagation
are addressed, while process selection, sampling, and polling settings remain
pending.
Verification details are in [PROGRESS.md](PROGRESS.md); the actionable checklist
is in [TODO.md](TODO.md).

The subsequent **0.14.0** update also replaces the generated webapp welcome page
with a Laravel-inspired light/dark UI, searchable commands/descriptions, a visible
AMEN version, project details, and a live
health-response inspector. See [WELCOME_DESIGN.md](WELCOME_DESIGN.md) for its
breakdown and screenshots. The resource generator below remains proposed.

## Recommended addition: a resource generator

Add **`amen add <app> resource <name>`** to generate a working database resource:
model, input/output schemas, CRUD endpoints, route registration, a migration
revision, and endpoint tests. This extends the existing endpoint generator and
gives developers a reason to keep using AMEN after project creation.

Proposed usage, unavailable in 0.13.1:

```bash
amen add myapp resource task --field title:str --field completed:bool=false --dry-run
amen add myapp resource task --field title:str --field completed:bool=false
```

For that example, generate `POST /tasks`, `GET /tasks`, `GET /tasks/{id}`,
`PATCH /tasks/{id}`, and `DELETE /tasks/{id}`. Flask should use Flask-SQLAlchemy
and validated request handling; FastAPI should use SQLAlchemy sessions and
Pydantic schemas. Return suitable creation/deletion statuses, validation errors,
and 404 responses. Include pagination and database transaction cleanup.

### First useful scope

1. Start with Flask + SQLite, a primary key, and string/integer/boolean fields.
2. Generate files and a migration revision; applying the migration remains an
   explicit action. Require an initialized migration environment or explain how
   to initialize one.
3. Preview all file writes with `--dry-run`. Refuse collisions by default and
   leave existing code intact when validation or generation fails.
4. Generate tests for create/list/read/update/delete, invalid input, and a
   missing record. Run them against an isolated test database.
5. Add FastAPI after its database/session/migration scaffolding is repaired;
   cover MySQL separately. Explain the requirement when the project has no DB.

**Acceptance:** on a freshly generated supported app, the preview changes no
files; generation registers the routes once; the reviewed migration creates the
table; all generated CRUD tests pass; rerunning the command preserves existing
user code. Document that generated CRUD routes need an explicit authorization
policy before use with private data.

**Prerequisites:** F01–F08 below, especially database initialization, model
discovery, real generated tests, safe writes, and project metadata.

**Rough effort:** 4–7 developer days for Flask/SQLite after prerequisites;
another 3–5 for FastAPI/MySQL parity. Estimates include regression tests and
documentation and are planning ranges, not commitments.

## Other additions worth making

| Addition | User benefit | Suggested scope | Rough effort |
| --- | --- | --- | --- |
| `amen doctor <app> [--json]` | Explains why an app cannot start or migrate | Check project metadata, interpreter, installed dependencies, entry point, environment keys, DB configuration, and port availability. Return nonzero for errors; do not modify files by default. | 1–2 days |
| Repeatable, unattended creation | Makes AMEN useful in CI, workshops, and team onboarding | Add `--database`, `--no-input`, `--output`, `--no-install`, and explicit overwrite handling. Validate all inputs before writing. Save the selected configuration. | 2–3 days |
| Dependency add/sync and usable offline installs | Makes projects reproducible on another machine | Persist direct dependencies, separate development tools, consume the existing cache, and provide an explicit lock/sync workflow. Define which Python/platform the offline cache supports. | 2–4 days |

Implement a small, versioned project manifest before these commands grow. It
should record the package name, framework, app type, database, Python requirement,
entry point, environment location, port, and scaffold version. Continue reading
legacy `.amen_config` projects. The exact file format is an implementation
decision; no metadata migration is performed by this review.

Defer additional frameworks, Docker/deployment generators, and full login/signup
scaffolding until the existing Flask/FastAPI workflows pass end-to-end checks.
`amen/auth.py` contains unused authentication boilerplate; its presence does not
establish a working authentication feature.

## Existing features that need fixing

Priorities: **P0** prevents silent loss of user code; **P1** fixes broken behavior
or unreliable results; **P2** improves portability, usability, and consistency.
“Runtime” means a disposable-project check; “mocked” means a command boundary or
platform value was substituted to isolate behavior; “inspection” means the code
path was reviewed without a full integration test.

### F01 — Restore FastAPI web-page rendering (P1)

**Runtime:** all three FastAPI webapp variants (no DB, SQLite, MySQL) import
and serve `/health`, but `GET /` raises `TypeError: unhashable type: 'dict'`
with FastAPI 0.149.0 / Starlette 1.9.0. The generated template call uses the old
positional argument order. The same call is emitted by `amen add ... view`.

**Evidence:** [manager.py:899](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/manager.py#L899),
[cli.py:567](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L567). The current
[FastAPI template documentation](https://fastapi.tiangolo.com/advanced/templates/)
shows explicit `request`, `name`, and `context` arguments.

**Fix:** emit `templates.TemplateResponse(request=request, name='index.html',
context={'title': app_name})` with the generated app name as the title. Use the
same convention in added views, and define/test compatible dependency versions.
The proposed change restored HTML responses in all three disposable webapps.

**Acceptance:** `GET /` and a newly added view return 200 HTML in a clean
FastAPI project; run against the supported dependency range. API-only root
responses must continue to pass. This fix is now implemented and regression-tested.

### F02 — Make database generation framework-aware (P1)

**Evidence:** [manager.py:32](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/manager.py#L32),
[manager.py:47](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/manager.py#L47),
[manager.py:943](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/manager.py#L943).

- **Runtime:** Flask with database `none` still initializes SQLAlchemy/Migrate
  with `mysql+pymysql://root@localhost/<app>`. This is a hidden database dependency,
  even though the landing and health routes can work without a DB connection.
- **Runtime/inspection:** FastAPI SQLite/MySQL projects receive a Flask `db.Model`
  implementation importing `db` from a package that does not define it. FastAPI
  has no generated engine, session dependency, or migration integration. All four
  DB-enabled FastAPI variants fail when their generated model module is imported.
- **Runtime:** Flask's initial model metadata is empty. Importing the generated
  models adds the `users` table, but application startup does not import them.
  Migration autogeneration therefore cannot discover the generated model.
- **Runtime/inspection:** `created_at` is evaluated during module import rather
  than per inserted row; generated requirements omit the model's `pytz` import.

**Fix:** generate DB setup per framework and database choice; omit it for
`none`; import models into migration metadata; use a callable timestamp default;
remove the timezone dependency or declare it. Separate migration initialization,
revision generation, and applying revisions. `amen migrate` currently always
uses Flask commands, including for FastAPI/no-DB projects
([cli.py:909](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L909)).

**Acceptance:** both frameworks import and serve `/health` with no DB installed
when `none` is selected. SQLite CRUD works; migration generation includes the
model; two inserts get independently computed timestamps. MySQL receives a
separate integration check against a disposable service. Unsupported migration
targets receive a clear nonzero error.

### F03 — Generate tests that exercise the application (P1)

**Runtime:** all **3 repository tests pass**, but coverage is **17%**. They call
the separate minimal `create_project()` helper, which only creates directories
and empty files; they do not call the actual `amen create` flow. Generated tests
contain `assert True` and `pass`, so three passing generated tests establish no
application behavior. The generated `pytest.ini` uses `[tool:pytest]`; pytest
9.1.1 runs the tests but ignores its intended options (`addopts` is empty).

**Evidence:** [test_project_creation.py:4](https://github.com/taqsblaze/amen-cli/blob/f447571/tests/test_project_creation.py#L4),
[cli.py:100](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L100),
[manager.py:766](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/manager.py#L766).

**Fix:** share the real creation service across CLI, web, and tests. Generate
Flask/FastAPI client fixtures and assertions for `/`, `/health`, missing/invalid
tokens, and DB behavior. Use `[pytest]` in `pytest.ini`. Add a pull-request test
workflow; the current workflow only builds/publishes on release.

**Acceptance:** a broken health endpoint fails a generated test. Test actual
Click commands and all framework × app-type × database generation combinations;
use a MySQL service for integration coverage. Exercise supported Python versions
and Linux/macOS/Windows paths in CI.

### F04 — Honor environment settings and make starter defaults safer (P1)

**Runtime/inspection:** Flask's application signing key is the literal
`your-secret-key`, while JWT verification reads `SECRET_KEY` from the environment.
The generated `.env` advertises `PORT` and `DATABASE_URL`, but the runners and
Flask DB configuration do not consume those settings. Every project receives
the same placeholder environment secret. `.env.example` and `.gitignore` are
documented but never generated.

**Evidence:** [manager.py:55](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/manager.py#L55),
[manager.py:142](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/manager.py#L142),
[manager.py:328](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/manager.py#L328),
[manager.py:828](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/manager.py#L828).

**Fix:** load configuration before constructing the app; use one secret source;
generate a unique local secret, a placeholder `.env.example`, and a `.gitignore`
covering `.env`, environments, caches, and generated local DB files. Read the
documented port/database variables consistently. Remove personal network/mail
defaults from generic scaffolds.

**Acceptance:** changing the configured port/database/secret changes behavior;
Flask signing and JWT verification use the same configured value; two new
projects have different secrets; local secrets are ignored by Git. Flask's
`app.run()` can load dotenv itself, so this finding does not claim that running
`python app.py` universally fails to load `.env`.

### F05 — Handle malformed authorization headers (P1)

**Runtime:** Flask `/protected` returns **500** for `Authorization: Bearer`:
the token decorator indexes `split(" ")[1]` before its error handler. A missing
header correctly returns 401, which the existing placeholder tests never check.

**Evidence:** [manager.py:817](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/manager.py#L817).

**Fix:** parse and validate the bearer scheme and token without unchecked
indexing. Keep authentication error responses consistent across both frameworks.

**Acceptance:** missing, empty, malformed, expired, and invalid tokens return
401; a valid token returns 200; malformed headers never produce a server error.

### F06 — Preserve user files during incremental scaffolding (P0)

**Runtime:** `amen add demo endpoint health` overwrites an existing custom
`demo/api/health.py` without confirmation. Endpoints, utilities, and templates
are written with unconditional `write_text()` calls.

**Evidence:** [cli.py:472](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L472),
[cli.py:490](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L490), [cli.py:544](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L544).

**Fix:** preflight every output and route registration, fail on collisions by
default, add a preview, and make replacement explicit. Avoid partial updates if
one output cannot be written. Project creation's existing-directory handling
also deletes the entire target tree after confirmation
([cli.py:303](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L303)); document the scope and validate the target
before reaching that operation.

**Acceptance:** existing endpoints/utilities/templates remain byte-for-byte
unchanged on a collision; no registration changes are left behind; a deliberate
replacement is explicit and reviewable.

### F07 — Validate Python names and register routes exactly (P1)

**Runtime/mocked:** creating `123demo` reports success but writes an invalid
Python import in `app.py` (environment creation/install were mocked).
`amen add demo endpoint class` also succeeds and writes invalid Python.
Adding an endpoint named `app` writes a file but never imports it: Flask
registration uses `if module_name in content`, and `app` already occurs in the
initializer.

**Evidence:** [cli.py:59](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L59),
[cli.py:281](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L281), [cli.py:456](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L456).

**Fix:** use `isidentifier()` plus keyword rejection and reserved-name checks;
separate the directory path from the importable package name; validate paths
before writes/deletion. Match imports/registrations structurally or with exact
generated markers, and report registration failures.

**Acceptance:** reject leading digits, Python keywords, path traversal, and
reserved module names before modifying files; allow valid names; every added
route is reachable once; rerunning generation does not duplicate registration.

### F08 — Return meaningful command and web results (P1)

**Runtime/mocked:** missing apps return exit **0** from `run`, `test`, `migrate`,
and `install`. A mocked server exit 7 and pytest exit 1 also produce CLI exit 0.
Creation returns normally when environment setup fails. The web creator returns
HTTP 200 with `status: success` for a blank name or failed environment setup;
its returned name can differ from the normalized directory name.

**Evidence:** [cli.py:319](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L319),
[cli.py:397](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L397), [cli.py:618](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L618),
[web.py:31](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/web.py#L31).

**Fix:** give creation a shared validated result/error contract; propagate child
exit statuses; use Click errors for failures; map validation/conflict/install
errors to suitable HTTP statuses. The web flow must not invoke terminal prompts
when a directory already exists. Run the server with an argument list instead
of `shell=True`, and surface captured installer/migration errors.

**Acceptance:** automation receives nonzero for failures; failed tests fail CI;
web failures do not report success; normalized project paths are returned;
directory conflicts produce a web response without waiting for terminal input.

### F09 — Repair security-audit severity filters (P1)

**Runtime/mocked:** `--severity high` builds `--severity-level h`. Bandit 1.9.4
rejects `h`, requiring `high`; `--severity h` instead raises `KeyError` because
the accepted alias is missing from AMEN's mapping. Audit failures are reported
with exit 0. Audit recursively includes the whole generated virtual environment.

**Evidence:** [cli.py:725](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L725),
[cli.py:749](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L749), [cli.py:757](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L757).
Bandit's accepted values are documented in its
[official CLI reference](https://bandit.readthedocs.io/en/latest/man/bandit.html).

**Fix:** normalize aliases to full severity names, exclude the environment and
generated caches, define exit statuses for findings versus tool failures, and
invoke Bandit from the CLI's Python environment. Preserve requested report data
without console decoration.

**Acceptance:** every accepted severity works with real Bandit; source findings
appear, environment dependencies are excluded, and tool failures have nonzero
status. Verify each advertised output format against the installed formatter.

### F10 — Make package installs reproducible and cache-aware (P1)

**Mocked/inspection:** `amen install` downloads into `~/.amen/package_cache`
but then calls plain `pip install <package>` without consuming that cache. It
leaves `requirements.txt` unchanged. Thus the documented offline-cache benefit
is not implemented by this command. Creation does try the cache first, but it
installs `FRAMEWORKS[framework]['packages']` before writing the complete generated
requirements; those two dependency lists can differ.

**Evidence:** [cli.py:223](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L223),
[cli.py:993](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L993),
[manager.py:315](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/manager.py#L315),
[frameworks.py:7](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/frameworks.py#L7).

**Fix:** resolve one dependency manifest, install it with the project's
interpreter, try AMEN's cache before the network, and persist explicit dependency
changes. Cache compatible artifacts and explain cache misses. Avoid downloading
the same dependencies again unnecessarily.

**Acceptance:** adding a package survives a clean reinstall; a prepared cache
works with network disabled; an incomplete cache fails clearly in offline mode
and falls back online when allowed. Verify generated imports in an isolated
environment containing only the generated requirements.

### F11 — Fix macOS executable paths (P1)

**Mocked:** `sys.platform = 'darwin'` makes the Python, pip, and Flask helpers
return `venv/Scripts/...`. macOS environments use `venv/bin/...`; the same Linux
versus-everything-else assumption exists in the web monitor helper.

**Evidence:** [cli.py:41](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L41),
[monitor_web.py:15](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/monitor_web.py#L15).

**Fix:** branch on Windows explicitly, use the environment's Python with
`-m pip`, `-m flask`, and `-m pytest`, and centralize path resolution.

**Acceptance:** actual Linux/macOS/Windows jobs can create, run, test, install,
and migrate a supported app. Native macOS/Windows execution was not performed
in this Linux review.

### F12 — Make monitoring select and sample the right process (P2)

**Runtime/mocked/inspection:** without `--port`, terminal monitoring always
selects `None`, so it displays Not Running. Refresh 0 or -1 produces an error
and exit 0. Web monitoring uses fixed port 5001 with debug enabled; the browser
polls every 1000 ms even when another refresh value is supplied. Process lookup
uses any connection on the selected port rather than identifying this project's
listening process. CPU is sampled during process discovery and immediately again
for display, so meaningful sampling intervals also need verification.

**Evidence:** [cli.py:840](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L840),
[cli.py:898](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L898),
[monitor_web.py:21](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/monitor_web.py#L21),
[monitor_web.py:75](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/monitor_web.py#L75),
[monitor.html:128](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/monitor.html#L128).

**Fix:** infer the app's configured port, validate a positive refresh interval,
track the listening process and sampling state, handle process exit/permission
errors, provide a separate dashboard port, and disable debug by default. Return
after the web-monitor flow so Ctrl+C does not start terminal monitoring.

**Acceptance:** an app on its default port is detected without `--port`; another
app/client is not mislabeled; CPU readings respond to sustained work; process
exit does not break the dashboard; polling honors refresh; one Ctrl+C stops it.

### F13 — Support headless configuration and environment-aware updates (P2)

**Mocked/inspection:** `config` requires a Tk desktop; failed Tk initialization
is swallowed and later references an undefined `root`. The exposed `--framework`
option is unused. Update compares versions only for inequality, so an installed
0.13.1 and reported 0.12.0 are described as a new version. Update installation
always adds `--user`, which is incompatible with a normal isolated virtualenv
(confirmed by a no-network pip dry run).

**Evidence:** [editor.py:12](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/editor.py#L12),
[cli.py:694](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L694), [cli.py:645](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L645).

**Fix:** support `$VISUAL`/`$EDITOR` and text-based get/set; handle missing Tk
clearly; remove or implement the unused option. Compare parsed versions and
choose an update strategy appropriate to how the CLI was installed.

**Acceptance:** configuration works over SSH without a display; a higher
installed version is never offered a downgrade; updates are verified in an
isolated environment and package-manager-owned installations receive suitable
instructions. No real self-update was performed during the review.

### F14 — Align documentation and package metadata (P2)

**Inspection/runtime:** the README does not document `add`, `docs`, or `about`;
the changelog’s `add` syntax omits the required app argument.
README creation options mention Bottle/Pyramid even though the actual Click
choices contain only Flask/FastAPI; the documented web default is 3000 while
the command default is 5050. Generated structure/setup instructions reference
files that are absent. Generated READMEs also contain literal generator branch
code and examples for unrelated frameworks because a string delimiter is wrong
at [manager.py:409](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/templates/manager.py#L409). Dependency lists are
duplicated across `pyproject.toml`, `setup.py`, `requirements.txt`, and framework
definitions, with repeated entries.
`amen.__init__` calls `metadata.version()` without catching
`PackageNotFoundError`, so its fallback does not handle an uninstalled checkout.

**Evidence:** [README.md](../README.md), [CHANGELOG.md](../CHANGELOG.md),
[pyproject.toml](../pyproject.toml), [setup.py](../setup.py),
[__init__.py:4](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/__init__.py#L4),
[cli.py:802](https://github.com/taqsblaze/amen-cli/blob/f447571/amen/cli.py#L802).

**Fix:** use one authoritative package definition and shared framework
capabilities; publish command examples verified against `--help`; repair
generated README formatting and structure; handle missing installed metadata
if direct checkout imports are intended. Keep existing release history intact.

**Acceptance:** every published command example parses and matches behavior;
wheel/sdist metadata agree; a clean installed wheel serves bundled web assets.
The review successfully built a wheel and confirmed bundled HTML/static assets;
missing package assets are not a confirmed defect.

## Implementation order

Current phase: **five selected fixes implemented; remaining work proposed**.
F01, F02, F05, F08, and the file-protection portion of F06 are complete. The milestone
table below remains the broader improvement plan; milestones are not claimed
complete merely because these selected issues were addressed.

| Milestone | Deliverable | Exit criteria | Rough effort |
| --- | --- | --- | --- |
| 1. Protect work and expose failures | F06–F09, basic name/path validation and shared creation result | Collision tests preserve files; CLI/web failures are observable; audit severity works | 2–4 days |
| 2. Make generated apps dependable | F01–F05, F10–F11, real CLI/scaffold CI | Supported no-DB and SQLite flows work; migration metadata is complete; generated tests detect failures; platform checks pass | 4–7 days |
| 3. Establish project metadata and diagnostics | Versioned metadata, unattended creation, `doctor` | Legacy projects remain readable; creation needs no prompts when fully specified; doctor explains a broken project | 3–5 days |
| 4. Add resource generation | Flask/SQLite CRUD MVP, then framework/database parity | Preview, collision handling, migration, routes, and behavioral tests all work together | 4–7 days + 3–5 for parity |
| 5. Finish workflow consistency | F12–F14 and lock/sync follow-up | Monitoring/config/update/documentation match the supported environments | 2–4 days, plus dependency lock/sync scope |

These ranges overlap for shared fixes and should not be treated as a fixed sum.
Each runtime bug fix should include a regression test, and each milestone should
pass before the dependent feature work begins.
