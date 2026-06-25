"""`osdu-samples` command-line entry point.

    osdu-samples                 # run all read-only samples
    osdu-samples list            # list every sample
    osdu-samples get-welllog     # run one sample
    osdu-samples search-welllogs get-welllog   # run several

Flags:
    --write          enable opt-in write samples (or set DEMO_ALLOW_WRITES=true)
    --id <id>        operate on a specific WellLog id (overrides DEMO_WELLLOG_ID)
    --verbose        turn on SDK request/response debug logging
"""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv
from osdu_python_client import OsduClient, OsduError, enable_debug_logging

from . import welllogs  # noqa: F401  (registers all samples via import side effect)
from .config import DemoOptions, SampleConfigError
from .context import SampleContext
from .registry import Sample, all_samples, get


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="osdu-samples", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("names", nargs="*",
                   help="sample name(s) to run, 'list', or nothing for all read-only samples")
    p.add_argument("--write", action="store_true", help="enable opt-in write samples")
    p.add_argument("--id", dest="id_override", default="", help="WellLog id to operate on")
    p.add_argument("--curves", default="",
                   help="repro-wide-welllog: comma-separated curve counts to sweep, e.g. 100,200,400,600")
    p.add_argument("--verbose", action="store_true", help="enable SDK debug logging")
    return p


def _print_list() -> None:
    width = max(len(s.name) for s in all_samples())
    print("Available samples:\n")
    for s in all_samples():
        mark = " (writes)" if s.writes else ""
        print(f"  {s.name.ljust(width)}  {s.description}{mark}")
    print("\nRun-all (no args) executes the read-only samples; add --write for the rest.")


def _resolve(names: list[str], allow_writes: bool) -> list[Sample]:
    if not names:
        return [s for s in all_samples() if not s.writes or allow_writes]
    resolved: list[Sample] = []
    for name in names:
        s = get(name)
        if s is None:
            sys.exit(f"Unknown sample '{name}'. Run 'osdu-samples list' to see options.")
        resolved.append(s)
    return resolved


def _run_one(sample: Sample, ctx: SampleContext, allow_writes: bool) -> bool:
    if sample.writes and not allow_writes:
        print(f"\n[skip] '{sample.name}' is a write sample; pass --write to run it.")
        return True
    ctx.heading(sample.name)
    try:
        sample.run(ctx)
        return True
    except SampleConfigError as e:
        print(f"  [config] {e}")
    except OsduError as e:
        print(f"  [OSDU error] {e}")
    except Exception as e:  # noqa: BLE001 — samples should never crash the whole run
        print(f"  [error] {type(e).__name__}: {e}")
    return False


def main(argv: list[str] | None = None) -> int:
    # Load `.env` into the environment so the samples' DEMO_* vars are visible.
    # (osdu-python-client reads .env via pydantic-settings for its own config only,
    # which does not export these keys to os.environ.)
    load_dotenv()

    args = _build_parser().parse_args(argv)

    if args.names == ["list"]:
        _print_list()
        return 0

    if args.verbose:
        enable_debug_logging()

    demo = DemoOptions.from_env()
    allow_writes = args.write or demo.allow_writes
    samples = _resolve(args.names, allow_writes)

    try:
        curve_counts = tuple(int(x) for x in args.curves.split(",") if x.strip())
    except ValueError:
        sys.exit("--curves must be a comma-separated list of integers, e.g. 100,200,400")

    ok = True
    with OsduClient() as osdu:  # config + auth from .env / environment
        ctx = SampleContext(osdu=osdu, demo=demo, id_override=args.id_override,
                            curve_counts=curve_counts)
        for s in samples:
            ok &= _run_one(s, ctx, allow_writes)
    print()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
