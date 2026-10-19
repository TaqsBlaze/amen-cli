# AMEN improvement backlog

Checked items are implemented; unchecked items remain proposed. See
[ROADMAP.md](ROADMAP.md) for evidence, acceptance criteria, dependencies, and
rough effort. Review baseline: 0.13.1 / `f447571`, 2026-10-19.

## First: preserve user work and report failures

- [x] **F06 / P0:** refuse endpoint, utility, and template collisions before
  writing; use exclusive file creation and roll back new output on failures.
- [ ] Add preview and explicit replacement options as a later enhancement.
- [ ] **F07 / P1:** validate package/module names and paths; register generated
  routes exactly once.
- [x] **F08 / P1:** propagate command failures and child exit codes; give CLI
  and web creation a shared result contract; remove terminal prompts from web
  conflict handling.
- [x] **F09 / P1:** fix Bandit severity mapping, exclude virtual environments,
  preserve machine-readable stdout, and distinguish findings from tool failure.
- [ ] Verify each advertised audit output formatter in integration checks.

## Next: make the supported scaffolds dependable

- [x] **F01 / P1:** update FastAPI template response calls in initial and added
  views; verify generated and added HTML responses with current dependencies.
- [x] **F02 / P1:** honor no-DB selection, generate framework-specific database
  setup, load model metadata, repair timestamps/dependencies, and dispatch
  migrations to Flask-Migrate or Alembic. SQLite migrations are integration-tested.
- [ ] Separate migration initialization/revision/application into explicit actions.
- [ ] **F03 / P1:** test actual CLI creation, generate behavioral tests, fix the
  generated pytest section, and add pull-request CI.
- [ ] **F04 / P1:** apply environment settings consistently; generate distinct
  local secrets, `.env.example`, and `.gitignore`.
- [x] **F05 / P1:** return 401 for malformed, invalid, and expired Flask bearer
  credentials; preserve valid-token responses and unrelated application errors.
- [ ] **F10 / P1:** install from one generated manifest, consume the package
  cache, and persist added dependencies.
- [ ] **F11 / P1:** resolve executable paths correctly on macOS and Windows;
  exercise native platform workflows in CI.

## New capabilities after their prerequisites pass

- [ ] Introduce versioned project metadata while preserving legacy
  `.amen_config` compatibility.
- [ ] Add unattended creation with explicit database/output/install options.
- [ ] Add read-only `amen doctor <app>` with readable/JSON reports and useful
  error exit codes.
- [ ] Add `amen add <app> resource <name>` for Flask/SQLite, including a preview,
  validated CRUD routes, model, migration revision, and behavioral tests.
- [ ] Extend resource generation to FastAPI and MySQL after their database and
  migration integration checks pass.
- [ ] Define a dependency lock/sync workflow and its offline compatibility
  guarantees.

## Workflow and documentation follow-up

- [ ] Publish the authorized 0.14.0 GitHub release and verify its package workflow.

- [x] Redesign generated Flask/FastAPI webapp welcome pages with local assets,
  accessible interactions and real health inspection; prepare version 0.14.0.
- [x] Revise the welcome page to the requested Laravel-like design, remove the
  illustration, highlight AMEN version, and list commands with descriptions.
- [x] Validate monitor refresh/port values, propagate foreground web-monitor
  startup errors, and return after web monitoring stops.
- [ ] **F12 / P2:** infer the monitored port, retain sampling state, honor browser
  polling settings, make the dashboard port configurable, and disable debug.
- [ ] **F13 / P2:** support terminal editors/configuration and installation-aware
  updates with parsed version comparisons.
- [ ] **F14 / P2:** align command examples, repair generated READMEs, consolidate
  package metadata, and handle uninstalled-checkout version lookup if supported.

## Verification still required during implementation

- [ ] Native macOS and Windows execution.
- [ ] MySQL connectivity, schema creation, and migration upgrades against a
  disposable server.
- [ ] Fresh generated-project environments installed solely from their own
  dependency manifests.
- [ ] Network-disabled cache hit/miss integration checks.
- [ ] Full self-update behavior in disposable installation modes.

The remaining checks above are implementation/release acceptance work, not
claimed completed verification. SQLite migrations and generated-project route
checks are covered by the new regression suite.
