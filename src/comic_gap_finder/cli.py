from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .core import scan_directory
from .output import validate_outputs, write_report, write_stdout
from .render import render_json, render_markdown


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="comic-gap-finder",
        description="Find likely issue-number gaps from local comic filenames.",
    )
    result.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    result.add_argument("root", type=Path)
    result.add_argument(
        "--expectations", type=Path, help="JSON per-series ranges and omission reasons"
    )
    result.add_argument("--recursive", action="store_true")
    result.add_argument("--expected-start", type=int)
    result.add_argument("--expected-end", type=int)
    result.add_argument("--json", dest="json_path", type=Path)
    result.add_argument("--markdown", type=Path)
    result.add_argument("--fail-on-gaps", action="store_true")
    return result


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate expectations key: {key}")
        result[key] = value
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        report = scan_directory(
            args.root,
            recursive=args.recursive,
            expected_start=args.expected_start,
            expected_end=args.expected_end,
            expectations=json.loads(
                args.expectations.read_text(encoding="utf-8"), object_pairs_hook=unique_object
            )
            if args.expectations
            else None,
        )
        markdown = render_markdown(report)
        validate_outputs([path for path in (args.json_path, args.markdown) if path])
        if args.json_path:
            write_new(args.json_path, render_json(report))
        if args.markdown:
            write_new(args.markdown, markdown)
        if not args.json_path and not args.markdown:
            write_stdout(markdown + "\n")
        has_gaps = any(series.missing for series in report.series)
        return 1 if args.fail_on_gaps and has_gaps else 0
    except (OSError, TypeError, ValueError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def write_new(path: Path, content: str) -> None:
    target = path.expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    write_report(target, content)
