#!/usr/bin/env python3
"""Generate bilingual DLI National Training session pages from a CSV.

The committee edits one spreadsheet instead of hand-writing two Markdown files
per session and keeping their front matter in sync.

    # turn _data/sessions.csv into session pages
    python3 _scripts/generate_sessions.py

    # see what would change, without writing anything
    python3 _scripts/generate_sessions.py --dry-run

    # start a CSV from a year that already exists
    python3 _scripts/generate_sessions.py --export 2025

For each CSV row this writes _sessions/<archive>/en/<ref>.md and the matching
fr/<ref>.md, and scaffolds <archive>/en/<archive>.md and fr/<archive>.md if they
are missing.

Session descriptions: if a row's description_en / description_fr cell is empty,
the prose already in the file is kept. That makes it safe to re-run later just
to add YouTube links. Put <!--more--> in a description to mark where the excerpt
shown on the schedule listing should stop.

Standard library only, so it runs anywhere Python 3 does — including the GitHub
Actions runner that regenerates these files when the CSV changes.
"""

import argparse
import csv
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
CSV_PATH = REPO / "_data" / "sessions.csv"
LANGS = ("en", "fr")

REQUIRED = ["archive", "ref", "date", "hour", "weight", "title_en", "title_fr"]
OPTIONAL = [
    "category", "presenter_en", "presenter_fr", "session_link", "youtube_link",
    "slides", "room", "location", "description_en", "description_fr",
]
COLUMNS = REQUIRED + OPTIONAL

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FRONT_MATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n?", re.DOTALL)

YEAR_PAGE_TITLES = {
    "en": "{year} National Training",
    "fr": "Formation nationale {year}",
}


def rel(path):
    """Path shown in messages: repo-relative when possible, else absolute."""
    try:
        return path.relative_to(REPO)
    except ValueError:
        return path


class ValidationError(Exception):
    """A problem in the CSV that the editor needs to fix."""


def yaml_str(value):
    """Quote a scalar so YAML always reads it back as the same string.

    Session titles contain '|', ':' and apostrophes, all of which are
    significant in YAML. A JSON string is valid YAML, so json.dumps is a safe
    and dependency-free way to emit one.
    """
    return json.dumps(value, ensure_ascii=False)


def read_rows(csv_path):
    """Read and validate the CSV, returning a list of row dicts."""
    if not csv_path.exists():
        raise ValidationError(
            "No CSV found at %s.\n"
            "Create one, or run with --export <year> to generate it from an "
            "existing year." % rel(csv_path)
        )

    with csv_path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise ValidationError("%s is empty." % rel(csv_path))

        headers = [h.strip() for h in reader.fieldnames]
        missing = [c for c in REQUIRED if c not in headers]
        if missing:
            raise ValidationError(
                "%s is missing required column(s): %s\nExpected columns: %s"
                % (rel(csv_path), ", ".join(missing), ", ".join(COLUMNS))
            )

        rows = []
        seen = {}
        for lineno, raw in enumerate(reader, start=2):
            row = {
                (k.strip() if k else k): (v.strip() if isinstance(v, str) else "")
                for k, v in raw.items()
                if k is not None
            }
            if not any(row.get(c) for c in REQUIRED):
                continue  # blank spreadsheet row

            where = "%s line %d" % (rel(csv_path), lineno)
            for col in REQUIRED:
                if not row.get(col):
                    raise ValidationError("%s: '%s' must not be empty." % (where, col))

            if not row["archive"].isdigit() or len(row["archive"]) != 4:
                raise ValidationError(
                    "%s: 'archive' must be a 4-digit year, got %r."
                    % (where, row["archive"])
                )
            if not DATE_RE.match(row["date"]):
                raise ValidationError(
                    "%s: 'date' must look like 2026-05-06, got %r." % (where, row["date"])
                )
            try:
                int(row["weight"])
            except ValueError:
                raise ValidationError(
                    "%s: 'weight' must be a whole number, got %r." % (where, row["weight"])
                )
            if "/" in row["ref"] or " " in row["ref"]:
                raise ValidationError(
                    "%s: 'ref' becomes a filename and a URL, so it cannot contain "
                    "spaces or slashes. Got %r." % (where, row["ref"])
                )

            key = (row["archive"], row["ref"])
            if key in seen:
                raise ValidationError(
                    "%s: ref '%s' is already used for %s on line %d. Each ref must "
                    "be unique within a year." % (where, row["ref"], row["archive"], seen[key])
                )
            seen[key] = lineno

            row.setdefault("category", "")
            if not row["category"]:
                row["category"] = "presentation"
            rows.append(row)

    if not rows:
        raise ValidationError("%s has no data rows." % rel(csv_path))
    return rows


def existing_body(path):
    """Return the prose below the front matter of an existing file, if any."""
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    return FRONT_MATTER_RE.sub("", text, count=1)


def render_slides(value):
    """A single URL stays bare; several become a YAML list, matching past years."""
    urls = [u.strip() for u in value.split("|") if u.strip()]
    if not urls:
        return ""
    if len(urls) == 1:
        return urls[0]
    return "[" + ",".join(yaml_str(u) for u in urls) + "]"


def render_session(row, lang, body):
    """Build the full Markdown file for one session in one language."""
    presenter = row.get("presenter_%s" % lang, "").strip()
    lines = [
        "---",
        "title: %s" % yaml_str(row["title_%s" % lang]),
        "date: %s" % row["date"],
        "hour: %s" % row["hour"],
        # unquoted so Jekyll sorts the schedule numerically
        "weight: %d" % int(row["weight"]),
        "lang: %s" % lang,
        "ref: %s" % row["ref"],
        "presenter: [%s]" % presenter,
        "category: %s" % row["category"],
        # unquoted so it compares equal to the schedule page's `archive`
        "archive: %s" % int(row["archive"]),
    ]
    if row.get("room"):
        lines.append("room: %s" % yaml_str(row["room"]))
    if row.get("location"):
        lines.append("location: %s" % row["location"])
    lines += [
        "session_link: %s" % row.get("session_link", ""),
        "slides: %s" % render_slides(row.get("slides", "")),
        "youtube_link: %s" % row.get("youtube_link", ""),
        "---",
    ]
    # rstrip so empty values do not leave a trailing space after the colon
    out = "\n".join(line.rstrip() for line in lines) + "\n"
    if body.strip():
        out += "\n" + body.strip("\n") + "\n"
    return out


def render_year_page(year, lang):
    return (
        "---\n"
        "title: %s\n"
        "layout: sessions\n"
        "description:\n"
        "#intro_image: \"\"\n"
        "#intro_image_absolute: true\n"
        "#intro_image_hide_on_mobile: true\n"
        "lang: %s\n"
        "ref: %s\n"
        "archive: %s\n"
        "category: presentation\n"
        "---\n"
        % (YEAR_PAGE_TITLES[lang].format(year=year), lang, year, year)
    )


def write(path, content, dry_run, changes):
    """Write a file if its content would change, recording what happened."""
    before = path.read_text(encoding="utf-8") if path.exists() else None
    if before == content:
        return
    label = "update" if before is not None else "create"
    changes.append((label, rel(path)))
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def generate(csv_path, dry_run=False):
    rows = read_rows(csv_path)
    changes = []
    years = sorted({row["archive"] for row in rows})

    for row in rows:
        for lang in LANGS:
            path = REPO / "_sessions" / row["archive"] / lang / ("%s.md" % row["ref"])
            described = row.get("description_%s" % lang, "").strip()
            body = "\n" + described + "\n" if described else existing_body(path)
            write(path, render_session(row, lang, body), dry_run, changes)

    for year in years:
        for lang in LANGS:
            path = REPO / year / lang / ("%s.md" % year)
            if not path.exists():
                write(path, render_year_page(year, lang), dry_run, changes)

    print("%d session row(s) across year(s): %s" % (len(rows), ", ".join(years)))
    if not changes:
        print("Everything already up to date; nothing written.")
        return 0

    for label, rel in changes:
        print("  %-6s %s" % (label, rel))
    if dry_run:
        print("\n--dry-run: no files were written.")
    else:
        print("\n%d file(s) written." % len(changes))
        for year in years:
            if int(year) >= 2026:
                print(
                    "Reminder: set `current_year: %s` in _config.yml when %s becomes "
                    "the year being run." % (year, year)
                )
                break
    return 0


def parse_front_matter(path):
    """Pull the front-matter keys out of an existing session file."""
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, ""
    block = match.group(0).strip().strip("-").strip()
    data = {}
    for line in block.splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip()
    return data, FRONT_MATTER_RE.sub("", text, count=1).strip()


def unwrap(value):
    """Strip YAML quoting / list brackets back to plain spreadsheet text."""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        try:
            return " | ".join(json.loads("[%s]" % inner)) if inner else ""
        except (ValueError, TypeError):
            return inner
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        try:
            return json.loads(value)
        except ValueError:
            return value[1:-1]
    return value


def export(year, csv_path, dry_run=False):
    """Write a CSV describing a year that already has session files."""
    src = REPO / "_sessions" / str(year)
    if not src.is_dir():
        raise ValidationError("No session files found at %s." % rel(src))

    refs = sorted({p.stem for lang in LANGS for p in (src / lang).glob("*.md")})
    rows = []
    for ref in refs:
        row = {c: "" for c in COLUMNS}
        row["archive"], row["ref"] = str(year), ref
        for lang in LANGS:
            path = src / lang / ("%s.md" % ref)
            if not path.exists():
                print("  note: %s has no %s version" % (ref, lang.upper()))
                continue
            fm, body = parse_front_matter(path)
            row["title_%s" % lang] = unwrap(fm.get("title", ""))
            row["presenter_%s" % lang] = unwrap(fm.get("presenter", ""))
            row["description_%s" % lang] = body
            for key in ("date", "hour", "weight", "category", "session_link",
                        "youtube_link", "room", "location"):
                if fm.get(key):
                    row[key] = unwrap(fm[key])
            if fm.get("slides"):
                row["slides"] = unwrap(fm["slides"])
        rows.append(row)

    rows.sort(key=lambda r: (r.get("date", ""), int(r["weight"] or 0), r["ref"]))

    if dry_run:
        print("--dry-run: would write %d row(s) to %s"
              % (len(rows), rel(csv_path)))
        return 0

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print("Wrote %d row(s) from %s to %s"
          % (len(rows), rel(src), rel(csv_path)))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--csv", type=pathlib.Path, default=CSV_PATH,
                        help="CSV to read or write (default: _data/sessions.csv)")
    parser.add_argument("--export", metavar="YEAR",
                        help="write a CSV from the session files of YEAR instead of generating")
    parser.add_argument("--out-dir", type=pathlib.Path,
                        help="write generated pages under this directory instead of the repo "
                             "(for testing)")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would change without writing")
    args = parser.parse_args(argv)

    global REPO
    if args.out_dir:
        REPO = args.out_dir.resolve()

    try:
        if args.export:
            return export(args.export, args.csv, args.dry_run)
        return generate(args.csv, args.dry_run)
    except ValidationError as exc:
        print("Error: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
