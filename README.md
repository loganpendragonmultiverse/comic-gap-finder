# Comic Gap Finder

Comic Gap Finder scans local comic filenames for likely issue numbers, groups conservative series-name matches, and reports missing integers, duplicate numbers, decimal issues, and filenames too ambiguous to classify safely. It does not require an account or an external metadata service.

## Three-minute use

Python 3.10 or newer is required.

    python -m pip install "comic-gap-finder @ https://github.com/loganpendragonmultiverse/comic-gap-finder/releases/download/v1.0.0/comic_gap_finder-1.0.0-py3-none-any.whl"
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
