# Comic Gap Finder

Comic Gap Finder scans local comic filenames for likely issue numbers, groups conservative series-name matches, and reports missing integers, duplicate numbers, decimal issues, and filenames too ambiguous to classify safely. It does not require an account or an external metadata service.

## Three-minute use

Python 3.10 or newer is required.

    python -m pip install "comic-gap-finder @ https://github.com/loganpendragonmultiverse/comic-gap-finder/releases/download/v1.1.2/comic_gap_finder-1.1.2-py3-none-any.whl"
    comic-gap-finder "D:\Comics\Night Watch" --markdown gaps.md --json gaps.json
    comic-gap-finder "D:\Comics\Night Watch" --expected-start 1 --expected-end 50 --fail-on-gaps

Recognized containers are CBZ, CBR, CB7, PDF, ZIP, RAR, and 7Z. Explicit markers such as “#12” and “Issue 12” are preferred. A filename without a marker is accepted only when one non-year, non-volume number remains.

## Interpretation and privacy

This is a filename audit, not a completeness authority. Annuals, specials, skipped numbers, legacy numbering, reboots, decimal issues, variants, and deliberately absent issues require human review. The tool never opens archives, renames files, or looks up publication data.

Processing is read-only and local. Reports can reveal collection filenames, so review them before sharing.

## Development

    python -m pip install -e ".[dev]"
    ruff format --check .
    ruff check .
    mypy src tests
    pytest
    python -m build

Version 1.0.0 is feature complete for its conservative filename rules. Contributions follow [CONTRIBUTING.md](CONTRIBUTING.md), security reports follow [SECURITY.md](SECURITY.md), and the code is released under the [MIT License](LICENSE).

## More open-source projects

This project is part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Browse the catalog for other released tools, source repositories, live demos, and downloads.


## Version 1.1.0

Use `--expectations expectations.json` to apply a separate integer range to each named series:

```json
{"North Signal":{"start":1,"end":12,"omissions":{"7":"Number intentionally not collected"}}}
```

Series names use the existing normalized filename grouping. Duplicate normalized names are rejected. Each rule requires both bounds; it overrides the global range for that series. Configured series with no files are still reported. Omission reasons appear in JSON and Markdown and suppress only those missing integer numbers. They do not hide present files, duplicates, decimals, annuals, or ambiguous filenames. Global options and scans without a configuration keep their existing behavior. Bounds are limited to -1000 through 100000 (at most 101001 integer numbers per series). Decimal issues remain evidence, not integer range members. Annuals remain separate filename-inferred series; ambiguous identities require review.

## Version 1.1.2

Keep distinct non-Latin series separate and leave explicit issue ranges unresolved.

- Preserve Unicode letters and digits in grouping and exact decimal issue values; quarantine compound explicit issue numbers and reject duplicate expectation JSON keys.
- Reserve report files exclusively, preflight paired destinations, and render titles, paths and omission reasons literally in Markdown.

Reports contain local filenames and authored text. Markdown displays line breaks as literal `\n`/`\r`; JSON retains exact strings. Every output must be a distinct new path. Existing files, symlink destinations and a file created before exclusive opening are refused with exit 2. Both destinations are checked before writing, but paired reports are not a transaction: a later write or stdout failure can leave an earlier newly created report. Nothing is deleted automatically. Keep reports outside the scanned tree when repeating a scan.
