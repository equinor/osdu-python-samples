# Copilot instructions

Runnable, self-contained samples for `osdu-python-client` + `osdu-python-models`,
centred on **Wellbore DDMS well logs**. Each sample doubles as documentation, so
keep them small and readable.

## Environment & commands

Uses [uv](https://docs.astral.sh/uv/). `osdu-python-client` and
`osdu-python-models` are **editable path dependencies from sibling checkouts**
(`[tool.uv.sources]` in `pyproject.toml`) — clone all three under the same parent
directory or `uv sync` will fail to resolve them.

```sh
uv sync --extra dev              # install runtime + ruff/pytest
uv run ruff check src            # lint (rules: E,F,I,UP,B; line-length 110; py310 target)
uv run pytest -q                 # tests (none yet)
uv run pytest tests/test_x.py::test_name   # run a single test once tests exist
```

Running samples (prefix with `uv run`, or `source .venv/bin/activate`):

```sh
uv run osdu-samples                        # all read-only samples
uv run osdu-samples list                   # list every sample
uv run osdu-samples get-welllog            # one; multiple names run several
uv run osdu-samples ingest-welllog --write # write samples are opt-in
```

Flags: `--write` (or `DEMO_ALLOW_WRITES=true`) enables write samples; `--id`
overrides `DEMO_WELLLOG_ID`; `--curves` feeds `repro-wide-welllog`; `--verbose`
turns on SDK debug logging.

## Configuration split

Two config domains, read by different owners:

- `SERVER` / `DATA_PARTITION_ID` / `AUTH_*` — owned and read by
  `osdu-python-client` (via pydantic-settings; these do **not** land in
  `os.environ`). Auth defaults to interactive MSAL with a token cache.
- `DEMO_*` — owned by these samples (`config.DemoOptions.from_env`). `cli.main`
  calls `load_dotenv()` explicitly so `DEMO_*` are visible in `os.environ`.

Copy `.env.example` to `.env` (gitignored). Read samples need only the connection
block + `DEMO_WELLLOG_ID` (or `--id`); write samples also need `DEMO_WELLBORE_ID`,
`DEMO_LEGAL_TAG`, `DEMO_ACL_OWNER`, `DEMO_ACL_VIEWER`.

## Architecture

- **Registry pattern** (`registry.py`): every sample is a `run(ctx: SampleContext)`
  function decorated with `@sample("name", "description", writes=<bool>)`, stored
  in an insertion-ordered dict.
- **Import order == run/display order.** Samples are registered purely by being
  imported in `welllogs/__init__.py` (isort disabled there). Placement in that
  import list controls the order of `list` and run-all, mirroring the C# samples.
- **`SampleContext`** (`context.py`) is the single handle each sample gets: the
  live `OsduClient`, resolved `DemoOptions`, `--id` override, and `heading`/`kv`
  print helpers. `well_log_id` resolves `--id` over `DEMO_WELLLOG_ID`.
- **`cli.py`** loads `.env`, resolves sample names, opens one `OsduClient` context
  manager, and runs each sample. `_run_one` catches `SampleConfigError`,
  `OsduError`, and any `Exception` so one failing sample never aborts the run.

## Conventions

- **Typed-model bridge.** The client keeps record `data` free-form (a dict,
  matching OSDU `Map<String, Object>`); `osdu-python-models` adds typed Pydantic
  models per kind+version. Cross the boundary with these two calls only:
  - Write: `data_model.model_dump(by_alias=True, exclude_none=True)` → dict →
    `build_record(...)` (see `welllogs/_common.py`).
  - Read: `Data.model_validate(record_data_dict(record))` (see
    `context.record_data_dict`, which handles model-or-dict `data`).
- Samples target **WellLog schema `1.4.0`**: `osdu_models.workproductcomponent.well_log.v1_4_0`;
  kind constant `WELLLOG_KIND` in `_common.py`.
- Bulk curve data (`/data`) is **Parquet**; use the client's
  `read_bulk_parquet` / `write_bulk_parquet` helpers (needs the `parquet` extra).
- Mark anything that creates/updates/deletes with `writes=True`.
- Read inputs from `ctx.demo` / `ctx.well_log_id`; fail with friendly messages via
  `ctx.require_well_log_id()` / `ctx.demo.require(...)` (raise `SampleConfigError`),
  not bare exceptions.
- Commits follow **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, ...).

## Adding a sample

1. New module in `src/osdu_samples/welllogs/` with one `run(ctx)` decorated with
   `@sample(...)`.
2. Add it to the import list in `welllogs/__init__.py` at its intended position.
3. Set `writes=True` if it mutates data.
4. Add a row to the samples table in `README.md`.
