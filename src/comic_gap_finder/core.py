from __future__ import annotations

import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .models import ParsedComic, ScanReport, SeriesReport

COMIC_EXTENSIONS = {".cbz", ".cbr", ".cb7", ".pdf", ".zip", ".rar", ".7z"}
EXPLICIT = re.compile(r"(?i)(?:^|[\s._-])(?P<label>#|issues?|no\.?)\s*(?P<number>-?\d+(?:\.\d+)?)")
NUMBER_TOKEN = re.compile(r"(?<![A-Za-z0-9])(?P<number>\d+(?:\.\d+)?)(?![A-Za-z0-9])")
VOLUME_TOKEN = re.compile(r"(?i)(?:^|[\s._-])(?:v|vol(?:ume)?)\s*\d+\b")
YEAR_TOKEN = re.compile(r"^(?:19|20)\d{2}$")
NOISE = re.compile(r"(?i)\b(?:digital|webrip|scan|fixed|retail|variant|cover)\b")


def scan_directory(
    root: Path,
    *,
    recursive: bool = False,
    expected_start: int | None = None,
    expected_end: int | None = None,
    expectations: dict[str, object] | None = None,
) -> ScanReport:
    scan_root = root.expanduser().resolve()
    if not scan_root.is_dir():
        raise ValueError(f"scan root is not a directory: {scan_root}")
    if expected_start is not None and expected_end is not None and expected_start > expected_end:
        raise ValueError("expected start cannot be greater than expected end")

    rules = validate_expectations({} if expectations is None else expectations)
    validate_bound(expected_start)
    validate_bound(expected_end)

    candidates = scan_root.rglob("*") if recursive else scan_root.glob("*")
    parsed: list[ParsedComic] = []
    ambiguous: list[str] = []
    ignored: list[str] = []
    for path in sorted(candidates):
        if not path.is_file():
            continue
        relative = path.relative_to(scan_root)
        if path.suffix.casefold() not in COMIC_EXTENSIONS:
            ignored.append(relative.as_posix())
            continue
        result, reason = parse_filename(relative)
        if result is None:
            ambiguous.append(f"{relative.as_posix()}: {reason}")
        else:
            parsed.append(result)

    grouped: dict[str, list[ParsedComic]] = defaultdict(list)
    display_names: dict[str, str] = {}
    for comic in parsed:
        key = normalize_series(comic.series)
        grouped[key].append(comic)
        display_names.setdefault(key, comic.series)

    reports = []
    for key in sorted(set(grouped) | set(rules)):
        name, start, end, omissions = rules.get(
            key, (display_names.get(key, key), expected_start, expected_end, {})
        )
        reports.append(
            build_series_report(
                name, grouped[key], expected_start=start, expected_end=end, omissions=omissions
            )
        )
    return ScanReport(scan_root, reports, ambiguous, ignored)


def parse_filename(path: Path) -> tuple[ParsedComic | None, str]:
    stem = path.stem
    explicit = list(EXPLICIT.finditer(stem))
    if len(explicit) == 1:
        match = explicit[0]
        issue = decimal_issue(match.group("number"))
        if issue is None:
            return None, "invalid explicit issue number"
        series = clean_series(stem[: match.start()] or stem[match.end() :])
        if not series:
            return None, "series name could not be inferred"
        return ParsedComic(path, series, issue, "explicit marker"), ""
    if len(explicit) > 1:
        return None, "multiple explicit issue numbers"

    without_volume = VOLUME_TOKEN.sub(" ", stem)
    candidates = []
    for match in NUMBER_TOKEN.finditer(without_volume):
        token = match.group("number")
        if YEAR_TOKEN.match(token):
            continue
        number = decimal_issue(token)
        if number is not None:
            candidates.append((match, number))
    if len(candidates) != 1:
        return None, "no unique unmarked issue number"
    match, issue = candidates[0]
    series = clean_series(without_volume[: match.start()] or without_volume[match.end() :])
    if not series:
        return None, "series name could not be inferred"
    return ParsedComic(path, series, issue, "single number token"), ""


def build_series_report(
    name: str,
    comics: list[ParsedComic],
    *,
    expected_start: int | None,
    expected_end: int | None,
    omissions: dict[int, str] | None = None,
) -> SeriesReport:
    ordered = sorted(comics, key=lambda comic: (comic.issue, comic.path.as_posix().casefold()))
    by_issue: dict[Decimal, list[ParsedComic]] = defaultdict(list)
    for comic in ordered:
        by_issue[comic.issue].append(comic)
    integers = sorted(int(issue) for issue in by_issue if issue == issue.to_integral_value())
    if expected_start is not None:
        start = expected_start
    else:
        start = integers[0] if integers else 0
    if expected_end is not None:
        end = expected_end
    else:
        end = integers[-1] if integers else -1
    validate_bound(start)
    validate_bound(end)
    if end >= start and end - start + 1 > 101001:
        raise ValueError("expected range exceeds 101001 issues")
    present = set(integers)
    omitted = omissions or {}
    missing = [
        issue for issue in range(start, end + 1) if issue not in present and issue not in omitted
    ]
    duplicates = {
        format(issue, "f"): [comic.path.as_posix() for comic in matches]
        for issue, matches in sorted(by_issue.items())
        if len(matches) > 1
    }
    non_integer = [
        format(issue, "f") for issue in sorted(by_issue) if issue != issue.to_integral_value()
    ]
    return SeriesReport(name, ordered, missing, duplicates, non_integer, omitted)


def decimal_issue(value: str) -> Decimal | None:
    try:
        number = Decimal(value)
    except InvalidOperation:
        return None
    if not number.is_finite() or number < -1000 or number > 100000:
        return None
    return number.normalize()


def clean_series(value: str) -> str:
    cleaned = re.sub(r"[\[\](){}]", " ", value)
    cleaned = NOISE.sub(" ", cleaned)
    cleaned = re.sub(r"[_\-.]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_series(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def validate_bound(value: int | None) -> None:
    if value is not None and (type(value) is not int or not -1000 <= value <= 100000):
        raise ValueError("expected bounds must be integers between -1000 and 100000")


def validate_expectations(
    data: dict[str, object],
) -> dict[str, tuple[str, int | None, int | None, dict[int, str]]]:
    if not isinstance(data, dict):
        raise TypeError("expectations must be a series-name object")
    result = {}
    for name, rule in data.items():
        key = normalize_series(name)
        if not key or key in result or not isinstance(rule, dict):
            raise ValueError("empty, duplicate normalized series or invalid rule")
        if set(rule) - {"start", "end", "omissions"}:
            raise ValueError("unknown expectation field")
        start, end = rule.get("start"), rule.get("end")
        validate_bound(start)
        validate_bound(end)
        if start is None or end is None or start > end:
            raise ValueError("each series requires ordered start and end integers")
        raw = rule.get("omissions", {})
        if not isinstance(raw, dict):
            raise TypeError("omissions must map integer issue numbers to reasons")
        omitted = {}
        for number, reason in raw.items():
            if not isinstance(number, str) or not re.fullmatch(r"-?\d+", number):
                raise ValueError("omission numbers must be integer strings")
            issue = int(number)
            if issue in omitted or not start <= issue <= end:
                raise ValueError("duplicate omission or issue outside expected range")
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError("each intentional omission requires a reason")
            omitted[issue] = reason.strip()
        result[key] = (name, start, end, omitted)
    return result
