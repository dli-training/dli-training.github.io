# DLI National Training — website editing guide

The site at **<https://dli-training.github.io/>** is built from this repository with
[Jekyll](https://jekyllrb.com/) and published automatically by GitHub Pages.

This guide is written for Professional Development Committee members. You do **not** need to
install anything — every task below can be done in the browser on GitHub.

- [How publishing works](#how-publishing-works)
- [The three rules](#the-three-rules)
- [Editing in your browser](#editing-in-your-browser)
- [Adding a year's sessions from a spreadsheet](#adding-a-years-sessions-from-a-spreadsheet)
- [The spreadsheet columns](#the-spreadsheet-columns)
- [Editing one session by hand](#editing-one-session-by-hand)
- [Session field reference](#session-field-reference)
- [Common tasks](#common-tasks)
- [Starting a new training year](#starting-a-new-training-year)
- [Showing and hiding menu items](#showing-and-hiding-menu-items)
- [Previewing the site on your own computer](#previewing-the-site-on-your-own-computer-optional)
- [Troubleshooting](#troubleshooting)
- [Where everything lives](#where-everything-lives)

---

## How publishing works

Every commit pushed to the **`master`** branch is picked up by GitHub Pages, which rebuilds the
site and publishes it. There is no separate deploy step.

Changes normally appear **within one to two minutes**. If you don't see your edit, give it a
moment and then do a hard refresh (<kbd>Shift</kbd> + reload). You can watch the build status
under the repository's **Actions** tab.

`master` is the live site, so an edit pushed to `master` is a published edit. If you want a second
pair of eyes first, make your changes on a branch and open a pull request instead.

## The three rules

**1. Everything is bilingual.** Almost every file has an English and a French twin. If you edit
one, edit the other, or the site falls out of sync for French visitors.

| English | French |
| --- | --- |
| `en/contact.md` | `fr/contact.md` |
| `_sessions/2025/en/1-rds.md` | `_sessions/2025/fr/1-rds.md` |
| `2025/en/2025.md` | `2025/fr/2025.md` |

The spreadsheet workflow below handles this for you — it writes both languages from one row.

**2. A session's `ref:` must match its filename.** The EN/FR toggle in the navigation builds the
other language's address out of `archive` + `lang` + `ref`. If `_sessions/2025/en/2-update.md`
says `ref: 1-update`, that toggle points at a page that doesn't exist.

This is easy to get wrong by copying a file and forgetting to change `ref`, and it was the cause
of two broken toggles on the live site. The spreadsheet workflow takes `ref` straight from the
filename, so it cannot drift.

**3. The block at the top of each file is front matter.** Everything between the opening `---`
and closing `---` is configuration, not page text. Keep both `---` lines, keep the field names
exactly as they are, use spaces rather than tabs. Your words go *below* the closing `---`.

```markdown
---
title: "S1 | Research Data Service (RDS)"
date: 2025-05-06
lang: en
---

This text, below the second `---`, is what visitors read.
```

## Editing in your browser

1. Open the file on GitHub — for example [`en/contact.md`](en/contact.md).
2. Click the pencil icon (**Edit this file**).
3. Make your change.
4. Scroll down, write a short note in the commit message box, and click **Commit changes**.
5. Repeat for the French twin, unless you used the spreadsheet.

GitHub also has a full editor: press <kbd>.</kbd> while viewing the repository, or change
`github.com` to `github.dev` in the address bar.

## Adding a year's sessions from a spreadsheet

**This is the recommended way to add a programme.** Instead of hand-writing two Markdown files
per session, you fill in one row per session in [`_data/sessions.csv`](_data/sessions.csv) and the
site builds the files for you — both languages, every field kept in sync.

### The browser route (no software needed)

1. Open [`_data/sessions.csv`](_data/sessions.csv) on GitHub and click the pencil icon. (You can
   also download it, edit in Excel or Google Sheets, and upload it back — it is an ordinary CSV.)
2. Add one row per session. See [the columns](#the-spreadsheet-columns) below.
3. Commit to `master`.
4. A GitHub Action called **Generate session pages** runs automatically, writes the session files,
   and commits them. The site rebuilds a minute later.

Watch it under the **Actions** tab. If something in the spreadsheet is wrong — a missing date, a
duplicated `ref`, a weight that isn't a number — the Action **fails and writes nothing**, and the
log tells you which line and which column to fix. Nothing reaches the live site until it is valid.

If you open a pull request instead of committing to `master`, the Action only checks the
spreadsheet and reports problems; it does not write any files.

### The local route

If you prefer to work on your own computer, run the generator yourself:

```bash
python3 _scripts/generate_sessions.py
```

Useful options:

| Command | What it does |
| --- | --- |
| `python3 _scripts/generate_sessions.py` | Build the session files from the spreadsheet |
| `python3 _scripts/generate_sessions.py --dry-run` | Show what would change, write nothing |
| `python3 _scripts/generate_sessions.py --export 2025` | Write the spreadsheet *from* an existing year |

`--export` is how to get started: point it at a year that already exists and it gives you a filled-in
spreadsheet to copy rows from. It only reads, never writes session files.

It needs Python 3, which macOS and Linux already have. No libraries to install.

### Safe to re-run

Running the generator again does not undo your work:

- If a row's `description_en` / `description_fr` cell is **empty**, the prose already in the file is
  **kept**. So after the event you can paste YouTube links into the spreadsheet, re-run, and the
  session descriptions survive untouched.
- If nothing has changed, it writes nothing and says so.

`_data/sessions.csv` currently holds the real 2025 programme, as a worked example to copy from.

## The spreadsheet columns

| Column | Required | What it does |
| --- | --- | --- |
| `archive` | yes | The year, e.g. `2026`. Decides which folder the session lands in and which schedule page lists it. |
| `ref` | yes | Short name, e.g. `1-rds`. Becomes the filename **and** the last part of the web address, so no spaces or slashes. Must be unique within a year. |
| `date` | yes | `YYYY-MM-DD`. Sessions are grouped under a heading per date. |
| `hour` | yes | Free text shown beside the title, e.g. `13:00 ET`. Include the timezone. |
| `weight` | yes | A whole number. Sort order within the day; lower comes first. |
| `title_en` / `title_fr` | yes | The session title in each language. |
| `category` | no | Defaults to `presentation`, which is what puts a session on the schedule. |
| `presenter_en` / `presenter_fr` | no | `Name (Institution), Name (Institution)`. Separate per language because institutions are translated — *Statistics Canada* / *Statistique Canada*. |
| `session_link` | no | Zoom join URL. Not displayed at present — see the note in the field reference. |
| `youtube_link` | no | Adds a "Watch on YouTube" link to the sidebar. |
| `slides` | no | One URL, or several separated by `\|`. Shown as *Document #1*, *#2*, … |
| `room` | no | In-person location. |
| `location` | no | URL the room name links to, e.g. a campus map. |
| `description_en` / `description_fr` | no | The session description. Leave blank to keep whatever is already in the file. Put `<!--more-->` where the excerpt shown on the schedule should stop. |

Long descriptions make a cell span several lines in the raw file. That is normal CSV and
spreadsheets handle it correctly.

## Editing one session by hand

For a one-off tweak, editing the Markdown directly is still perfectly fine — the generator only
touches rows that are in the spreadsheet. Just remember rules 1 and 2: change both languages, and
leave `ref` matching the filename.

Each session is two files with the same name:

```
_sessions/2025/en/1-rds.md
_sessions/2025/fr/1-rds.md
```

The filename becomes the address: `_sessions/2025/en/1-rds.md` is published at
`https://dli-training.github.io/2025/en/1-rds/`.

Between the two files, only `title`, `lang` and the description should differ. Everything else —
`date`, `hour`, `weight`, `ref`, `archive`, `category`, links — must match exactly.

## Session field reference

| Field | What it does |
| --- | --- |
| `title` | Heading and schedule link text. Quoted, because titles contain `\|`, `:` and apostrophes, which are meaningful in YAML. |
| `date` | `YYYY-MM-DD`. Groups sessions under a date heading. |
| `hour` | Free text beside the title. Not parsed, so include the timezone. |
| `weight` | Sort order within the day. Lower first. Must be a bare number, not quoted. |
| `lang` | `en` or `fr`. The one field that differs between the pair. |
| `ref` | Links the EN and FR versions. **Must equal the filename** without `.md`. |
| `category` | Must be `presentation` to appear on the schedule and for the language toggle to work. |
| `archive` | The year, **unquoted** (`2025`, never `"2025"`). Decides which schedule and archive page lists it. |
| `presenter` | A bracketed list: `[Name (Institution), Name (Institution)]`. |
| `slides` | One URL, or a list. Shown as *Document #1*, *#2*, … |
| `youtube_link` | Adds a "Watch on YouTube" link. |
| `room` / `location` | In-person location, and a URL for it. Only shown if `room` is set. |
| `session_link` | Zoom URL. **Currently not displayed** — the "JOIN ZOOM SESSION" button in `_includes/sidebar.html` is commented out. Uncomment it to use. |

The sidebar labels ("Presented by:", "Watch on YouTube", …) are not in the session files — they are
translated once in `_data/menus.yml`.

### How sessions reach the schedule

Sessions are not listed by hand. The Schedule page (`en/program.md`) and each year's archive page
(`2025/en/2025.md`) declare what they want:

```yaml
category: presentation
archive: 2025
```

The page collects every session whose `lang`, `category` **and** `archive` match its own, groups
them by `date`, and orders them by `weight`.

## Common tasks

### Update the committee contact list

The members list is plain Markdown at the bottom of `en/contact.md` and `fr/contact.md`. Email
addresses in angle brackets become links:

```markdown
### Atlantic Region

Sam Read : <sread@stfx.ca>
Sandra Sawchuk : <sandra.sawchuk@msvu.ca>
```

Two trailing spaces at the end of a line force a line break — that is why each name sits on its own
line. Without them Markdown runs the names into one paragraph.

### Change the text on a page

The main pages are in `en/` and `fr/`:

| File | Page |
| --- | --- |
| `index.md` | Home |
| `program.md` | Schedule |
| `archive.md` | Event Archive — the year cards are generated; see below |
| `resources.md` | Resources |
| `contact.md` | Contact |
| `register.md` | Registration |
| `feedback.md` | Feedback |
| `workshop.md` | Workshops |
| `call-in.md` | Call-in details |
| `local.md` | Local information |
| `bio.md` | Presenter bios |
| `404.md` | Page-not-found |

Several contain large blocks wrapped in `<!-- ... -->`. That is HTML comment syntax: the text stays
in the file but is hidden from visitors, which is how past announcements are parked for reuse. To
bring a block back, delete the `<!--` before it and the `-->` after it. To retire a block, wrap it
the same way rather than deleting it.

Watch for the nested and unclosed comment markers already in `en/program.md` — if text there
appears or disappears unexpectedly, a stray `<!--` is the likely cause.

### Add slides or recordings after the event

Put the links in the `slides` and `youtube_link` columns of the spreadsheet and commit. Blank
description cells mean the existing session text is preserved.

To do it by hand instead, edit both language files:

```yaml
slides: https://docs.google.com/presentation/d/FILE_ID/edit
youtube_link: https://youtu.be/VIDEO_ID
```

Check that Google Drive sharing allows anyone with the link to view.

### The Event Archive page

`en/archive.md` and `fr/archive.md` no longer list the years by hand. The page renders one card per
training year, newest first, reading the years straight from the session files and showing how many
sessions each year lists. A new year appears as soon as its sessions exist.

Anything you type in the body of those two files appears above the cards, so you can add an
introductory line. The card styling lives in `_sass/components/_archive-cards.scss` and the page
template in `_layouts/archive.html`.

### Update the date box on the home page

Dates and the registration button come from `_data/contact.yml`. The box itself is currently
**switched off** — it lives in `_layouts/home.html` inside a `<!--- ... --->` comment. Remove those
markers to switch it back on.

### Change the contact email

`email:` in `_config.yml` feeds the "Email us!" link.

> After editing `_config.yml`, a local preview must be stopped and restarted — Jekyll does not
> reload that file automatically. This does not affect GitHub Pages.

## Starting a new training year

Using 2026 as the example:

1. **Add the sessions** to [`_data/sessions.csv`](_data/sessions.csv) with `archive` set to `2026`,
   and commit. The generator writes the session files **and creates the year's two archive pages**
   (`2026/en/2026.md`, `2026/fr/2026.md`) for you.

2. **Point the Schedule page at the new year.** In `en/program.md` and `fr/program.md`, change
   `archive: 2025` to `archive: 2026`.

3. **Bump the year in `_config.yml`:**

   ```yaml
   current_year: 2026
   ```

   This one setting tells the site which year is live. Sessions in the current year link back to
   the Schedule; earlier years link back to their own archive page. Nothing else needs a per-year
   entry — the breadcrumbs build their links from each session's own `archive` value.

   The **Event Archive** page needs nothing: it builds its year cards from the session files, so
   the new year appears there on its own.

4. **Refresh the home page**: the dates in `_data/contact.yml`, and the announcement text in
   `en/index.md` / `fr/index.md`.

5. **Re-enable the menu items** you need for an active event — Schedule, Registration, Feedback.
   See below.

## Showing and hiding menu items

The navigation is defined in `_data/menus.yml`. Between events most items are commented out with
`#`. The live menu is whichever `- title:` / `url:` pairs are **not** commented:

```yaml
  links:
  #  - title: "Feedback"
  #    url: /en/feedback/
    - title: "Resources"
      url: /en/resources/
```

To show an item, remove the `#` from both of its lines and line the indentation up with its
neighbours. To hide one, add `#` to both lines. YAML is strict about indentation — spaces only,
never tabs. Do it in both the `en` and `fr` blocks. `footer:` lower down controls the footer links.

## Previewing the site on your own computer (optional)

Only needed for larger changes. You will need [Ruby](https://www.ruby-lang.org/) and Git.

```bash
git clone git@github.com:dli-training/dli-training.github.io.git
cd dli-training.github.io
bundle install
bundle exec jekyll serve --livereload
```

Then open <http://localhost:4000>. Pages rebuild as you save, except `_config.yml`, which needs a
restart.

A build prints a long list of Sass deprecation warnings from the bundled Bootstrap. These are
harmless — the build succeeded if it ends with `done in N seconds`.

Don't commit the `_site/` folder; it is generated output and is already in `.gitignore`.

## Troubleshooting

**My change isn't on the live site.**
Wait two minutes, then hard-refresh. Check the **Actions** tab for a failed build, and confirm you
committed to `master`.

**The spreadsheet Action failed.**
Open the run under **Actions** and read the error — it names the line and the column. Nothing was
written, so fix the CSV and commit again. Common causes: a date that isn't `YYYY-MM-DD`, a `weight`
that isn't a number, two rows sharing a `ref` in the same year, an empty required cell.

**A new session isn't on the schedule.**
Check `category: presentation`; `archive:` matching the schedule page's `archive:` and unquoted;
`lang:` matching the page you are looking at; and `date:` in `YYYY-MM-DD` form.

**The EN/FR toggle on a session page gives a 404.**
The twin file is missing, or its `ref:` does not match the filename. See rule 2.

**A page shows raw text, or the layout collapses.**
Front matter is broken. Check both `---` lines are present, no tabs, and that any value containing
a colon is wrapped in double quotes.

**Text I wrote isn't appearing.**
It is probably inside an HTML comment. Search the file for `<!--`.

**The whole build fails after my edit.**
A YAML error in `_config.yml` or `_data/` can stop the build. Revert the last commit (open it on
GitHub and click **Revert**), then reapply the change more carefully.

## Where everything lives

```
├── _config.yml          Site title, email, current_year. Restart local preview after editing.
├── _data/
│   ├── sessions.csv     The editable programme — one row per session
│   ├── menus.yml        Navigation, footer, sidebar labels
│   └── contact.yml      Home page date box and registration button
├── _scripts/
│   └── generate_sessions.py   Turns sessions.csv into session pages
├── .github/workflows/
│   └── generate-sessions.yml  Runs that script automatically when the CSV changes
├── _sessions/           Generated session content, by year then language
├── 2020/ … 2025/        One archive landing page per year, per language
├── en/, fr/             The main pages
├── _layouts/            Page templates (archive.html builds the year cards)
├── _includes/           Reused fragments (header, sidebar, breadcrumbs, menus)
├── _sass/               Styles, including bundled Bootstrap and the archive cards
├── assets/              CSS, JavaScript, fonts
├── images/              Logos and illustrations
└── _site/               Generated output — never edited, never committed
```

Files and folders starting with `_` belong to Jekyll and are not published as pages.

### Known gaps

Six 2020 sessions (`0-dli-update`, `1-pumf`, `2-dmp`, `2-lightning`, and the two
`data-visualization` workshops) have no `date:` or `archive:` in their front matter. Their pages
exist, but they are not listed on the 2020 archive page and their EN/FR toggles do not resolve.
Fixing this means adding the correct dates, which are not recorded anywhere in the repository.

---

## Credits

- Beautiful royalty free Illustrations by Icons8 - https://icons8.com/illustrations/style--pixeltrue
