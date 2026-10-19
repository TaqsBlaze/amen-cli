# Review and implementation progress

## 2026-10-19 — Commit and release preparation

Completed

- User authorized committing the accumulated source/tests/docs, pushing main,
  and creating the 0.14.0 GitHub release.
- Fetched remote branches/tags and confirmed main has no incoming commits.
- Rechecked version0.14.0, release notes, full-suite result (245 passed), browser
  QA and locally built distributions; checked expected files and whitespace.
- Prepared a detailed commit/release description covering UI, database, safe
  scaffolding, failures, auth, validation and compatibility.
- Confirmed the existing release-published workflow builds packages and attempts
  PyPI publication; notified the user. No workflow changes were introduced.

Next

- Commit and push main, tag v0.14.0, publish GitHub release with wheel/sdist,
  then verify release state and the triggered build/publication workflow.

## 2026-10-19 — Laravel-inspired welcome revision

Completed

- Implemented the user's design correction: warm neutral/charcoal surfaces,
  Laravel-style red accents, compact welcome panel and a flat command grid.
  Removed the right-hand sculpture, preview canvas and obsolete art tokens.
- Made **AMEN v0.14.0** visible beside the logo, in project details and footer.
  The version remains 0.14.0 while refining the same unpublished release.
- Replaced three command tabs with sixteen documented, copyable examples:
  all thirteen CLI commands, three `add` variants and global help. Commands use
  actual project names, framework-aware monitor ports and a separate docs port.
- Added progressive search across titles, syntax and descriptions, accessible
  result counts and empty/reset states. All examples remain visible without JS.
  Preserved theme preference, copy fallback, health JSON and error/retry handling.
- Extended the existing welcome tests to check complete command coverage and
  syntax through Click contexts without invoking commands, version prominence,
  descriptions, source visibility and removal of the illustration.
- Updated README, design breakdown, shared docs, release notes and changelog;
  refreshed both screenshots. This entry supersedes the initial visual direction
  recorded below; all previous database/auth/command repairs remain intact.

### Validation

| Check | Result |
| --- | --- |
| Full repository suite | **245 passed in 102.17s; 76% total coverage** |
| Focused welcome suite | **10 passed in 21.84s**, covering both frameworks and every DB choice |
| Command reference | All sixteen examples parse; every real CLI command, valid project arguments and selected framework ports covered |
| Browser layouts/accessibility | 1440/768/390/320px × light/dark; no horizontal overflow; eight WCAG A/AA scans with zero reported violations |
| Browser behavior | Search matching/counts/empty/reset, keyboard focus, copy success/denial, themes/storage denial, JS-disabled command visibility, health disclosure and all six error/recovery cases passed |
| Version and long names | Header version visible at every tested width; long project names remain contained |
| Runtime | No browser script errors or external runtime asset requests; reduced-motion behavior passed |
| Packaging/hygiene | 0.14.0 wheel and sdist build; bundled welcome assets match source; Python formatting, JS syntax, local doc links and whitespace checks pass; tracked coverage unchanged |

Browser tooling and the reproducible session harness live outside the repository
at `/tmp/amen-ui-qa/revision-check.cjs`; raw results/audits use `revision-*` names.
Current screenshots are in `docs/images/`. The owned preview server is stopped
at teardown. No release was published or existing project page overwritten.

Limits remain native Safari/Firefox/older-browser, macOS/Windows, deployment
subpath and live MySQL verification. Automated accessibility checks supplement
manual visual/keyboard work rather than establishing full conformance.

## 2026-10-19 — Premium welcome UI and 0.14.0

Completed

- Replaced the default generated Flask/FastAPI webapp page with a shared,
  responsive design: warm neutral surfaces, green accents, local Instrument Sans,
  native SVG artwork/icons, clear next steps and complete light/dark themes.
- Added keyboard-operated command tabs, actual app-specific command examples,
  clipboard success/manual-copy feedback, saved/system theme selection and
  accessible focus/status states. Motion respects the reduced-motion setting.
- Added genuine same-origin `/health` checks with manual refresh, HTTP status,
  measured duration and a JSON disclosure. Connection/HTTP/JSON/body-read errors
  and request/body timeouts clear old responses and permit retry.
- Packaged HTML, tokens, CSS, JavaScript, WOFF2 and the SIL OFL license. Generator
  writes preserve font bytes; older common-file CSS/JS output no longer replaces
  these assets. Metadata substitution is HTML/Jinja-safe and framework-aware.
- Fixed preview-canvas sizing and header spacing discovered during 320px phone
  QA. Long project names wrap or truncate within their intended containers.
- Added ten regression cases covering webapp framework/database combinations,
  local assets/MIME, font/license, command targets, API JSON and escaping.
- Updated both version declarations to **0.14.0**, changelog and release notes
  for the UI feature and accumulated repairs. Refreshed editable metadata and
  confirmed `amen about` reports 0.14.0.
- Added [WELCOME_DESIGN.md](WELCOME_DESIGN.md), light/dark screenshots and README
  guidance; synchronized shared contracts, decisions and backlog.

### Verification

| Check | Result |
| --- | --- |
| Full repository suite | **245 passed in 110.45s; 76% total coverage** |
| Focused welcome suite after final CSS/JS adjustments | **10 passed in 21.68s** |
| Chromium layouts | 1440, 768, 390 and 320px in both themes; no document overflow; preview contained within card |
| Automated accessibility | Eight WCAG A/AA scans; **zero reported violations** |
| Browser interactions | Keyboard arrows/Home/End, copy/permission-denied fallback, theme persistence/system changes/storage denied, health JSON disclosure, reduced motion and JavaScript-disabled content passed |
| Health failures | HTTP 503, invalid JSON, network failure, body-read error, request timeout and body timeout all showed errors, cleared stale healthy JSON and recovered on retry |
| Browser runtime | No JavaScript errors or remote asset requests |
| Extra responsive checks | Long app names at four widths and a half-width desktop viewport remained contained |
| Package build | 0.14.0 wheel and sdist built; all eight welcome/database helper and asset files match source bytes; sdist includes design docs/screenshots |
| Installed-wheel probe | Imported AMEN from a separate wheel install; generated Flask/FastAPI no-DB apps served 0.14.0 HTML, styles, scripts, WOFF2 and license |
| Hygiene | New Python modules/tests pass Black; JavaScript syntax, local Markdown links and `git diff --check` pass; tracked coverage artifact unchanged |

Commands/tooling used:

```bash
COVERAGE_FILE=/tmp/amen-014-coverage /tmp/amen-review-venv/bin/python -m pytest
/tmp/amen-review-venv/bin/python -m pytest tests/test_welcome_page.py --no-cov
/tmp/amen-review-venv/bin/python -m build --no-isolation \
  --outdir /tmp/amen-014-final-dist
node --check amen/templates/welcome/welcome.js
git diff --check
```

Browser QA used disposable Node Playwright/axe tooling and Chromium outside the
repository against a generated Flask project. The maintained Python suite covers
both frameworks. Browser screenshots are in `docs/images/`; the temporary QA
harness and raw audit reports are under `/tmp/amen-ui-qa/` for this session.
The owned preview server was stopped during teardown.

Limits and next work

- Existing generated projects are not rewritten; API-only roots stay JSON.
- No package was published, release tagged or project deployed.
- Accessibility scans do not establish full conformance. Native Safari/Firefox,
  older browsers, Windows/macOS, deployment subpaths and live MySQL remain
  unverified. The wheel probe reused review-environment dependencies rather
  than testing dependency installation from scratch.
- Continue the remaining items in [TODO.md](TODO.md); the proposed resource
  generator is separate from this completed welcome-page update.

## 2026-10-19 — Baseline review at f447571

Completed

- Reviewed baseline `f447571` / version 0.13.1; the initial working tree was
  clean and `git pull --ff-only` reported already up to date.
- Inspected every CLI command, framework definitions, template generation,
  authentication boilerplate, web creator/monitor, editor, packaging, release
  workflow, and repository tests. Two reviewers coordinated through these
  documents; only the primary reviewer edited repository documentation.
- Created a disposable environment at `/tmp/amen-review-venv`; generated projects
  and probe scripts were kept in temporary directories.
- Ran the existing tests: **3 passed, 17% total coverage**. The tests exercise
  the minimal helper rather than the actual creation command.
- Exercised 12 generated combinations: Flask/FastAPI × API/webapp ×
  none/SQLite/MySQL. Imported apps and queried routes using framework test
  clients; MySQL connections were not opened.
- Checked CLI command boundaries with Click's test runner and mocked failing
  subprocesses, installer calls, platform values, and setup failures.
- Built a wheel without build isolation and verified six bundled asset paths:
  creator/monitor/docs HTML, JavaScript, CSS, and PNG.
- Documented 14 grouped findings, recommended resource generation plus smaller
  follow-up features, and wrote a dependency-ordered implementation backlog.
- Linked the review from the main README. Application code remains unchanged.
- Verified documentation links, finding identifiers, code fences, and whitespace;
  restored the tracked coverage artifact produced by the baseline test run.

### Verification results

| Check | Result |
| --- | --- |
| Existing repository suite | 3 passed; 17% total coverage |
| Generated app imports | 12/12 imported successfully |
| Generated `/health` | 12/12 returned 200 |
| Generated homepages | 9 returned 200; all 3 FastAPI webapp variants raised `TypeError: unhashable type: 'dict'` |
| FastAPI rendering fix trial | Explicit `request`, `name`, `context` restored 200 HTML in all 3 temporary webapps; no repository code changed |
| Missing authentication header | All variants returned 401 |
| Malformed `Authorization: Bearer` | All 6 Flask variants returned 500; all 6 FastAPI variants returned 401 |
| Valid JWT with explicit environment secret | All 12 protected routes returned 200 |
| Flask no-database choice | Still configured a MySQL SQLAlchemy engine |
| Flask model discovery, DB variants | All 4 started with empty metadata; manual model import added `users`; timestamp default was a scalar |
| FastAPI model imports, DB variants | All 4 failed to import nonexistent package `db` |
| Generated test scaffold | 3 placeholder tests passed; generated `pytest.ini` options were ignored (`addopts=[]`) |
| Generated setup files | `.env.example` and `.gitignore` absent; README contained generator control-flow text |
| Incremental generation | Existing `health.py` overwritten; `app` route import skipped; `class` generated invalid Python |
| Invalid project name | `123demo` reported success but produced invalid runner syntax; setup/install mocked |
| CLI failure status | Missing apps and mocked server/test/setup failures returned exit 0 |
| Web creation results | Blank name and mocked setup failure returned HTTP 200 success; normalized names were misreported |
| Audit severity | AMEN built `--severity-level h`; real Bandit rejected it; accepted alias `h` raised `KeyError` in AMEN |
| Install flow | Mocked calls downloaded to AMEN cache then installed without cache flags; requirements unchanged |
| macOS paths | Mocked `darwin` selected Windows `Scripts` paths |
| Monitoring | Refresh 0/-1 returned errors with exit 0; captured web configuration used port 5001/debug; browser interval stayed 1000 ms |
| Version comparison | Mocked installed 0.13.1 / remote 0.12.0 was described as a new version |
| Virtualenv update flags | No-network pip dry run rejected `--user` in the isolated environment |
| Wheel assets | All six expected asset paths present |

### Reproducing the checks

The repository suite and disposable dependency environment can be recreated
from the repository root with:

```bash
python3 -m venv /tmp/amen-review-venv
uv pip install --python /tmp/amen-review-venv/bin/python \
  --index-url https://pypi.org/simple \
  -e '.[dev]' fastapi uvicorn httpx jinja2 pyjwt pymysql hatchling build
/tmp/amen-review-venv/bin/python -m pytest
/tmp/amen-review-venv/bin/amen --help
/tmp/amen-review-venv/bin/python -m build --wheel --no-isolation \
  --outdir /tmp/amen-review-wheels
```

Use a new temporary project directory for destructive/collision probes. The
route checks generated each scaffold with `TemplateManager.generate_structure`,
then loaded its app in a separate process rooted at that project. Flask used
`app.test_client()`; FastAPI used `fastapi.testclient.TestClient`. Tests queried
`/`, `/health`, and `/protected`, including malformed headers. Model checks
inspected metadata before/after importing the generated model module. Temporary
probe scripts are not part of the maintained repository test suite.

Relevant resolved versions: Python 3.13.5, Flask 3.1.3, FastAPI 0.149.0,
Starlette 1.9.0, SQLAlchemy 2.1.5, pytest 9.1.1, Bandit 1.9.4,
Jinja2 3.1.6, and httpx 0.28.1. These are the review environment, not a proposed
supported-version policy. The initial default-index pip setup stalled; using an
explicit public index through uv completed setup.

### Limits of the review

No native macOS/Windows runs, live MySQL integration, full migration application,
network-disabled install, real CLI self-update, or complete per-project isolated
dependency installs were performed. The shared review environment contained
both frameworks and CLI dependencies, so successful imports do not establish
complete generated requirements. No remote publishing, deployment, or messages
to external services were performed.

Next

- Implement the first milestone in [ROADMAP.md](ROADMAP.md), starting with
  no-clobber generation, name/path validation, observable errors, and audit
  filters. Add regression tests with runtime fixes.
- Complete the scaffold/database corrections before building the resource
  generator.

## 2026-10-19 — Three selected fixes

Completed

- **F02: database scaffolding.** Added framework-specific database/model/migration
  templates. No-database projects no longer initialize or depend on database
  libraries. Flask registers models before migration setup; FastAPI provides
  SQLAlchemy `Base`, an engine, request-scoped sessions, and Alembic scaffolding.
- Database configuration reads external/project `.env` `DATABASE_URL` values;
  relative SQLite locations are anchored to the project root. MySQL uses PyMySQL.
  Timestamps are computed in UTC per inserted row using the standard library.
- Framework installation and generated requirements now use one selector with
  database-aware packages and compatible SQLAlchemy/Flask-SQLAlchemy/Alembic bounds.
  Cancelling DB selection stops before directory modification.
- `amen migrate` invokes the project's Python and selects Flask-Migrate or
  Alembic. No-database, missing configuration/interpreter, and subprocess failures
  produce actionable nonzero errors. The existing generate-then-apply behavior
  is retained; no migration subcommand redesign is included.
- **F01: FastAPI rendering.** Updated both initial homepages and added views to
  use explicit template response arguments; generated FastAPI requires >=0.108.0.
- **F06: preserving user code.** Incremental scaffolding preflights every output
  and parent path, refuses existing files/directories/symlinks, creates files
  exclusively, preserves utility initializers, and rolls back new output after
  write or registration errors. Registration updates replace files atomically.
- Added 89 regression cases across generated applications, database behavior,
  migration dispatch, dependency selection, rendering, and collision handling.
- Updated README usage/database instructions, development test dependencies,
  changelog, roadmap statuses, backlog, shared context, and decisions. The original
  review remains recorded against its pinned baseline commit.

### Validation of the implementation

| Check | Result |
| --- | --- |
| Full repository suite | **92 passed in 56.90s; 49% total coverage** (baseline: 3 tests, 17%) |
| Full generated-app matrix | All 12 framework/type/database combinations imported, served `/health` and `/`, and registered DB models where selected |
| No-database isolation | Both frameworks imported while database-library imports were explicitly blocked; generated requirements omitted DB libraries |
| SQLite persistence | Both frameworks inserted/read records with independently computed timestamps |
| SQLite migrations | Real `amen migrate` created `users` and `alembic_version` tables for Flask and FastAPI |
| Database overrides | Environment and project `.env` values worked for both frameworks after changing the working directory |
| Incremental generation | File/directory/symlink conflicts, two-output view conflicts, repeated calls, initializer preservation, injected write failures, and injected registration failures passed |
| Added FastAPI view | Rendered HTTP 200 HTML through the actual generated router |
| Final focused rerun | **11 passed** after tightening Flask dependency bounds and explicitly closing test SQLite connections |
| Formatting and whitespace | Black checks passed for new regression suites, database templates, and framework configuration; touched legacy blocks formatted; `git diff --check` passed |
| Final wheel | Built successfully; includes the new database template module, existing web assets, and updated development metadata |

Commands used for the final checks:

```bash
COVERAGE_FILE=/tmp/amen-fix-coverage /tmp/amen-review-venv/bin/python -m pytest
/tmp/amen-review-venv/bin/python -m pytest tests/test_scaffolds.py \
  tests/test_cli_scaffolding.py -k 'migrate or requirements or installer' --no-cov
/tmp/amen-review-venv/bin/python -m black --check amen/frameworks.py \
  amen/templates/database.py tests/test_scaffolds.py \
  tests/test_cli_scaffolding.py tests/test_cli_migrations.py
/tmp/amen-review-venv/bin/python -m build --wheel --no-isolation \
  --outdir /tmp/amen-fix-wheels
git diff --check
```

Limits

- MySQL driver/configuration/model import coverage is included; no live MySQL
  connection or schema upgrade was attempted. Native macOS/Windows runs remain
  pending. The macOS executable-path finding is not part of these three fixes.
- New scaffolding fixes affect newly generated projects. Existing generated
  applications are not rewritten, and legacy FastAPI projects without Alembic
  configuration receive instructions rather than a Flask migration attempt.
- Generated applications' own tests remain placeholders. The new repository
  regression suite exercises their actual behavior; F03's broader generated-test
  and CI work remains pending.

Next

- Address the remaining identifier/registration validation, command/web results,
  audit filters, authentication/configuration, and platform findings in TODO.md.
- Add live MySQL/native-platform integration coverage and consider migration
  action separation and scaffold preview/replacement controls as follow-up work.

## 2026-10-19 — Command failures and Flask authentication

Completed

- **F08:** expected command failures now raise Click errors instead of printing
  an error and returning success. Missing projects/environments/configuration,
  creation/setup failures, editor failures, and server/tool startup errors are
  observable to scripts and CI.
- Failed application, pytest, installation, and migration subprocesses preserve
  their exit codes and captured diagnostics. Signal failures use `128 + signal`.
  Application launch uses an argument list instead of a shell. Optional cache
  misses still recover when installation succeeds.
- Creation returns the actual project `Path` only after every setup step and
  metadata write succeeds. Cancelled setup/overwrite/update operations return
  nonzero. Project names/choices are validated before writes; noninteractive
  existing targets raise a typed conflict without a confirmation prompt.
- Web creation validates JSON/fields, translates validation/conflict/setup errors
  to HTTP 400/409/500, checks the creation result, and returns the normalized name
  and path on success. Unexpected errors use a generic response plus server log.
- **F05:** generated Flask token decorators validate header structure and bearer
  scheme before indexing/decoding. Missing/malformed/invalid/expired credentials
  return JSON 401; normal and case/whitespace-varied valid tokens return 200.
  Only PyJWT token errors are caught; unrelated application failures propagate.
- Related audit handling now normalizes severity aliases, excludes the project
  environment, uses the CLI's Bandit module, preserves report stdout, and returns
  zero for clean reports, one for findings, or the tool error status.
- Monitor refresh/port validation rejects invalid input before startup. Its web
  server runs in the foreground so startup errors reach the CLI; stopping it
  cannot fall through to a second terminal monitor. Other monitor work remains
  on the backlog.
- Updated README, changelog, roadmap/backlog statuses, shared contracts, and
  implementation decisions. Previous database/rendering/file-protection repairs
  remain covered by the integrated suite.

### Validation

| Check | Result |
| --- | --- |
| New CLI failure suite | **75 passed**; covers failures, successful operations, and recoverable cache misses |
| New auth/web suites | **68 passed** across targeted runs: six Flask app/database variants and 62 web request/lifecycle cases |
| Full repository suite | **235 passed in 68.16s**, **76% total coverage**; prior baseline after the first repairs was 92 tests/49% |
| Real child-process exits | Actual generated runner scripts exited 0/7 and the CLI preserved those statuses |
| Real Bandit checks | Clean/source-finding reports produced 0/1, parsed as JSON; unsafe code inside the virtual environment was excluded |
| Generated Flask auth | Missing/blank/malformed/wrong-scheme/extra-token headers and expired/bad-signature/wrong-algorithm JWTs returned 401; valid tokens returned 200 |
| Web creation | Real creation service/scaffolder with mocked installation; invalid input 400, normalized target conflicts 409 without prompts, setup failures 500, normalized success 200 |
| Package and documentation checks | Wheel built successfully; new test files passed Black; `git diff --check` and local documentation checks passed |

Final full-suite command:

```bash
COVERAGE_FILE=/tmp/amen-failure-auth-coverage /tmp/amen-review-venv/bin/python -m pytest
/tmp/amen-review-venv/bin/python -m build --wheel --no-isolation \
  --outdir /tmp/amen-failure-auth-wheels
git diff --check
```

Limits

- Subprocess/update/startup error cases are mocked except the explicit real
  application exits and Bandit checks. No real self-update, external deployment,
  or package publication was performed.
- The authentication template fix applies to newly generated projects. Existing
  generated token decorators require a manual update.
- Native macOS/Windows, live MySQL, full updater installation strategy/version
  comparison, headless editor support, and remaining monitoring behavior remain
  pending. Generated applications' own placeholder tests remain a separate item.

Next

- Continue the remaining name/registration, generated-test/CI, configuration,
  platform, dependency synchronization, and monitoring items in TODO.md.
