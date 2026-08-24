# OSDU Python Samples

Runnable, focused examples of using the [`osdu-python-client`][client] and
[`osdu-python-models`][models] packages against OSDU — centred on **Wellbore
DDMS well logs**. Each sample is a small, self-contained module you can read as
documentation and run on its own. This is the Python twin of the C#
[`osdu-csharp-samples`][csharp].

[client]: https://github.com/equinor/osdu-python-client
[models]: https://github.com/equinor/osdu-python-models
[csharp]: https://github.com/equinor/osdu-csharp-samples

## Samples

| Name | Description | Writes? |
|---|---|---|
| `service-info` | Print Wellbore DDMS service info (`/about`). | |
| `search-welllogs` | Search for WellLog records by kind. | |
| `get-welllog` | Get a WellLog by id and read its `data` with typed schema models. | |
| `welllog-versions` | List all stored versions of a WellLog. | |
| `navigate` | Follow WellLog → Wellbore → Well via data references. | |
| `read-bulk-data` | Read a WellLog's bulk curve data as a table (`/data`). | |
| `bulk-statistics` | Get per-curve bulk-data statistics (`/data/statistics`). | |
| `create-welllog` | Create a WellLog from a typed schema model. | ✍️ |
| `write-bulk-data` | Write bulk curve data to a WellLog. | ✍️ |
| `ingest-welllog` | Ingest a WellLog (typed schema) and its bulk data from files. | ✍️ |
| `delete-welllog` | Delete a WellLog by id. | ✍️ |
| `repro-wide-welllog` | Reproduce the wide-WellLog (>N curves) ingestion timeout. | ✍️ |

These samples target **WellLog schema `1.4.0`** (the typed models come from
`osdu_models.workproductcomponent.well_log.v1_4_0`).

Bulk data (`/data`) is served by Wellbore DDMS as **Parquet** (the performant
primary format). The bulk samples use the client's `read_bulk_parquet` /
`write_bulk_parquet` helpers, which round-trip a `pyarrow.Table` or a pandas
`DataFrame`; these require the client's `parquet` extra (already pulled in as a
dependency of this project).

## Install

This project uses [uv](https://docs.astral.sh/uv/). `uv sync` creates the
virtualenv and installs everything (including `osdu-python-client[parquet]`,
`osdu-python-models`, and the `osdu-samples` command):

```sh
uv sync                # runtime deps
uv sync --extra dev    # + ruff/pytest for development
```

`osdu-python-client` and `osdu-python-models` are installed from PyPI like any
other dependency — no sibling checkouts needed. To try a sample against an
unreleased library change, point at a local checkout without committing it:

```bash
uv add --editable ../osdu-python-client
```

## Running

Prefix commands with `uv run` (or activate the env once with `source .venv/bin/activate`
after `uv sync` and drop the prefix):

```sh
uv run osdu-samples                 # run all read-only samples
uv run osdu-samples list            # list every sample
uv run osdu-samples get-welllog     # run one sample
uv run osdu-samples search-welllogs get-welllog   # run several
```

Flags: `--write` enables the opt-in write samples (or set `DEMO_ALLOW_WRITES=true`);
`--id <welllog-id>` operates on a specific WellLog id, overriding `DEMO_WELLLOG_ID`;
`--verbose` turns on the SDK's request/response debug logging.

`--id` makes the ingest → read-back demo flow config-free — paste the id printed by
`ingest-welllog` straight into the read commands:

```sh
uv run osdu-samples ingest-welllog --write
# → Created WellLog: dev:work-product-component--WellLog:<new-id>
uv run osdu-samples get-welllog read-bulk-data bulk-statistics --id dev:work-product-component--WellLog:<new-id>
uv run osdu-samples delete-welllog --id dev:work-product-component--WellLog:<new-id> --write   # clean up
```

## Reproducing the wide-WellLog timeout

`repro-wide-welllog` is a focused diagnostic: it sweeps a range of curve counts,
creates a metadata-only WellLog at each (typed authoring → `post_welllog_osdu`),
times the create call, and classifies the outcome — then deletes the records it
made. Neither Wellbore DDMS nor Storage caps the curve count or processes it
super-linearly, so a sharp threshold points at an environmental limit (a gateway
/ ingress body-size or upstream-timeout policy, or the DDMS→storage client
timeout). The classifier labels each row accordingly (`413` gateway body limit,
`502/504` upstream timeout, `~10s` DDMS→storage timeout, client/transport hang).

```sh
uv run osdu-samples repro-wide-welllog --write                 # default sweep 100,200,400,600,800
uv run osdu-samples repro-wide-welllog --write --curves 300,400,450,500
```

It needs the same write config as `create-welllog` (`DEMO_WELLBORE_ID`,
`DEMO_LEGAL_TAG`, `DEMO_ACL_OWNER`, `DEMO_ACL_VIEWER`). Add `--verbose` to see the
SDK's per-request retry/timeout behaviour.

## Configuration

Copy [`.env.example`](.env.example) to `.env` (gitignored) and fill it in, or
provide the same values as environment variables. The `SERVER` / `AUTH_*` block
is read by `osdu-python-client`; the `DEMO_*` block is read by these samples:

```ini
SERVER=https://your-osdu-instance.com
DATA_PARTITION_ID=your-partition
AUTH_PROVIDER=azure_msal
AUTH_MODE=interactive
CLIENT_ID=<client-id>
AUTHORITY=https://login.microsoftonline.com/<tenant-id>
SCOPES=<app-id-uri>/.default

DEMO_WELLLOG_ID=<partition>:work-product-component--WellLog:<id>:
DEMO_WELLBORE_ID=<partition>:master-data--Wellbore:<id>:
DEMO_LEGAL_TAG=<partition>-...-legaltag
DEMO_ACL_OWNER=data.default.owners@<partition>.<domain>
DEMO_ACL_VIEWER=data.default.viewers@<partition>.<domain>
```

Authentication uses interactive MSAL by default (browser on first run, then
silent renewal from the token cache). Read samples need only the connection block
plus `DEMO_WELLLOG_ID` (or `--id`); write samples additionally need `DEMO_WELLBORE_ID`,
`DEMO_LEGAL_TAG`, `DEMO_ACL_OWNER`, `DEMO_ACL_VIEWER`.

`ingest-welllog` reads a typed WellLog `data` document — the bundled
[`sample_data/welllog-data.json`](src/osdu_samples/sample_data/welllog-data.json)
unless `DEMO_WELLLOG_DATA_FILE` points elsewhere. It is deserialized into the typed
`WellLog:1.4.0` model; the ACL, legal tag and parent `WellboreID` come from the
`DEMO_*` config, so the bundled example works against any instance. The matching
bulk Parquet is synthesized in-code from the declared curve mnemonics.

## How it fits together

`osdu-python-client` keeps the record `data` block free-form (a `dict`), matching
the canonical OSDU `Map<String, Object>`. `osdu-python-models` adds typed,
validated Pydantic models for a specific kind + version. The bridge is one call —
`model_dump(by_alias=True, exclude_none=True)` — with no client changes:

```python
from osdu_models.workproductcomponent.well_log.v1_4_0 import Curve, Data

data = Data(WellboreID="...:master-data--Wellbore:x:", Curves=[Curve(Mnemonic="GR")])
record = build_record(data.model_dump(by_alias=True, exclude_none=True), ...)
osdu.wellbore_ddms.post_welllog_osdu(body=[record])
```

See [`welllogs/_common.py`](src/osdu_samples/welllogs/_common.py) and
[`welllogs/create_welllog.py`](src/osdu_samples/welllogs/create_welllog.py).

## Contributing

Contributions are welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Security

To report a security vulnerability, follow the process in
[`SECURITY.md`](SECURITY.md). Do not open a public issue.

## License

Licensed under the [Apache License 2.0](LICENSE).
