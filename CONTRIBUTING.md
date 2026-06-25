# Contributing

Thanks for your interest in improving the OSDU Python samples.

## Development setup

```sh
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
```

For working against unreleased changes in the libraries, install them editable
alongside this project:

```sh
pip install -e ../osdu-python-client[parquet] -e ../osdu-python-models -e .
```

## Adding a sample

1. Add a module under `src/osdu_samples/welllogs/` with a single
   `run(ctx: SampleContext)` function decorated with
   `@sample("name", "one-line description", writes=<bool>)`.
2. Register it by adding the module to the import list in
   `src/osdu_samples/welllogs/__init__.py` — **import order is display/run order**,
   so place it where it belongs in the table.
3. Mark anything that creates, updates or deletes data with `writes=True`; those
   only run under `--write`.
4. Add a row to the table in `README.md`.

Keep each sample small and readable — it doubles as documentation. Read inputs
from `ctx.demo` / `ctx.well_log_id`, and use `ctx.require_well_log_id()` /
`ctx.demo.require(...)` to fail with a friendly message when config is missing.

## Checks

```sh
ruff check src
pytest -q   # if/when tests are added
```

## Commit conventions

Commits follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, ...),
matching the sibling library repositories.
