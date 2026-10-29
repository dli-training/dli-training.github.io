# DLI National Training — website editing guide

The site at **<https://dli-training.github.io/>** is built from this repository with
[Jekyll](https://jekyllrb.com/) and published by GitHub Pages.

Every task in this guide can be done in the browser on GitHub. Nothing needs to be installed on your machine.

- [Starting a new training year](#starting-a-new-training-year)
- [Showing and hiding menu items](#showing-and-hiding-menu-items)
- [How publishing works](#how-publishing-works)
- [Rules that matter](#rules-that-matter)
- [Editing in your browser](#editing-in-your-browser)
- [Adding sessions from the spreadsheet](#adding-sessions-from-the-spreadsheet)
- [Spreadsheet columns](#spreadsheet-columns)
- [Editing one session by hand](#editing-one-session-by-hand)
- [Session fields](#session-fields)
- [Common tasks](#common-tasks)
- [Previewing on your own computer](#previewing-on-your-own-computer)
- [Troubleshooting](#troubleshooting)
- [Where everything lives](#where-everything-lives)

---

## Starting a new training year

Using 2026 as the example:

1. **Add the sessions** to [`_data/sessions.csv`](_data/sessions.csv) with `archive` set to `2026`,
   and commit. This writes the session files and creates `2026/en/2026.md` and `2026/fr/2026.md`.

2. **Point the Schedule at the new year.** In `en/program.md` and `fr/program.md`, change
   `archive: 2025` to `archive: 2026`. This is what moves the sessions onto the Schedule page.

3. **Set the current year** in `_config.yml`:

   ```yaml
   current_year: 2026
   ```

   Sessions in this year link back to the Schedule; earlier years link back to their own archive
   page.

4. **Update the home page**: the dates in `_data/contact.yml`, and the announcement text in
   `en/index.md` and `fr/index.md`.

5. **Re-enable the menu items** for an active event — Schedule, Registration, Feedback. See below.

The Event Archive page needs no change. Earlier years keep their pages whether or not their rows
are still in the spreadsheet.

## Showing and hiding menu items

The navigation is in `_data/menus.yml`. Between events most items are commented out with `#`. The
live menu is whichever `- title:` / `url:` pairs are not commented:

```yaml
  links:
  #  - title: "Feedback"
  #    url: /en/feedback/
    - title: "Resources"
      url: /en/resources/
```

To show an item, remove the `#` from both of its lines and line the indentation up with its
neighbours. To hide one, add `#` to both lines. Do it in both the `en` and `fr` blocks. YAML needs
spaces, never tabs. `footer:` lower down controls the footer links.

## How publishing works

Every commit pushed to **`master`** rebuilds and publishes the site. There is no separate deploy
step, and `master` is the live site.

Changes appear within one to two minutes. If you don't see yours, hard-refresh
(<kbd>Shift</kbd> + reload) and check the **Actions** tab for a failed build.

To have a change reviewed first, commit it to a branch and open a pull request instead.

## Rules that matter

**1. Everything is bilingual.** Almost every file has an English and a French twin. If you are editing by hand, edit both.

| English | French |
| --- | --- |
| `en/contact.md` | `fr/contact.md` |
| `_sessions/2025/en/1-rds.md` | `_sessions/2025/fr/1-rds.md` |
| `2025/en/2025.md` | `2025/fr/2025.md` |

The spreadsheet writes both languages from one row, so it keeps this rule for you.

**2. A session's `ref` must match its filename.** The EN/FR toggle builds the other language's
address from `archive` + `lang` + `ref`. If `_sessions/2025/en/2-update.md` says `ref: 1-update`,
that toggle leads nowhere. The spreadsheet takes `ref` from the filename, so it cannot drift.

**3. The block at the top of each file is front matter.** Everything between the opening `---` and
closing `---` is configuration, not page text. Keep both `---` lines, keep the field names exactly
as they are, and use spaces rather than tabs. Your words go below the closing `---`.

```markdown
---
title: "S1 | Research Data Service (RDS)"
date: 2025-05-06
lang: en
---

This text, below the second `---`, is what people read on the page.
```

## Editing in your browser

1. Open the file on GitHub — for example [`en/contact.md`](en/contact.md).
2. Click the pencil icon (**Edit this file**).
3. Make your change.
4. Write a short note in the commit message box and click **Commit changes**.
5. Repeat for the French twin, unless you used the spreadsheet.

For several files at once, press <kbd>.</kbd> while viewing the repository, or change `github.com`
to `github.dev` in the address bar.

## Adding sessions to the spreadsheet

Add one row per session to [`_data/sessions.csv`](_data/sessions.csv) and the site writes both
language files for you.

**In the browser:**

1. Open [`_data/sessions.csv`](_data/sessions.csv) and click the pencil icon. You can also download
   it, edit it in Excel or Google Sheets, and upload it back — it is an ordinary CSV.
2. Add one row per session. See [the columns](#spreadsheet-columns).
3. Commit to `master`.
4. The **Generate session pages** Action writes the session files and commits them. The site
   rebuilds a minute later.

If a row is wrong, the Action fails, writes nothing, and names the line and column in its log.
Nothing reaches the live site until the spreadsheet is valid. On a pull request the Action only
checks the spreadsheet; it writes nothing.

**On your own computer**, run it yourself. It needs Python 3 and no libraries.

| Command | What it does |
| --- | --- |
| `python3 _scripts/generate_sessions.py` | Write the session files from the spreadsheet |
| `python3 _scripts/generate_sessions.py --dry-run` | Report what would change, write nothing |
| `python3 _scripts/generate_sessions.py --export 2025` | Write the spreadsheet *from* an existing year |

Use `--export` to start from a year that already exists; it only reads.

### Re-running it

Re-run the generator as often as you like:

- A blank `description_en` / `description_fr` cell keeps the text already in the file. Adding
  recording links after an event will not overwrite session descriptions.
- If nothing changed, it writes nothing and says so.
- It never deletes. If you **rename** a row's `ref`, the files under the old name stay published
  and stay on the schedule. The generator lists them as orphans — delete the files it names.

`_data/sessions.csv` holds the 2025 programme as a worked example.

## Spreadsheet columns

| Column | Required | What it does |
| --- | --- | --- |
| `archive` | yes | The year, e.g. `2026`. Sets which folder the session lands in and which schedule lists it. |
| `ref` | yes | Short name, e.g. `1-rds`. Becomes the filename and the end of the web address, so no spaces or slashes. Unique within a year. |
| `date` | yes | `YYYY-MM-DD`. Sessions are grouped under a heading per date. |
| `hour` | yes | The start time, e.g. `13:00 ET` or `12:00-13:00 EST`. Begin it with a 24-hour time, since it also sets the order sessions appear in. Include the timezone. |
| `title_en` / `title_fr` | yes | The session title in each language. |
| `category` | no | Defaults to `presentation`, which is what puts a session on the schedule. |
| `presenter_en` / `presenter_fr` | no | `Name (Institution), Name (Institution)`. Separate per language, because institutions are translated. |
| `session_link` | no | Zoom join URL. Not displayed — see [Session fields](#session-fields). |
| `youtube_link` | no | Adds a "Watch on YouTube" button, and a Recording tag on the schedule. |
| `slides` | no | One URL, or several separated by `\|`. Listed as *Document #1*, *#2*, …, and adds a Materials tag. |
| `room` | no | In-person location. |
| `location` | no | URL the room name links to, e.g. a campus map. |
| `description_en` / `description_fr` | no | The session description, written in Markdown. Blank keeps what is already in the file. Put `<!--more-->` where the excerpt shown on the schedule should stop. |

A long description makes its cell span several lines in the raw file. That is valid CSV and
spreadsheets read it correctly.

### Formatting a description

Description cells are Markdown, so a session made up of several talks can be set out as a list
rather than as a run of paragraphs. Start each line with `- `, and wrap a title in `**` to make it
bold. Two spaces at the end of a line break it without starting a new bullet:

```
Two pre-recorded talks, followed by a live question and answer session.<!--more-->

- **Teaching Critical Data Literacy Through an "Adopt a Dataset" Activity**··
  Sonia Dhaliwal (Brock University)
- **Raiders of the Last R-k: Putting R into a PCCF+ Guide**··
  Alexandra Cooper (Queen's University), Jeremy Buhler (University of British Columbia)
```

(`··` marks the two trailing spaces.) Everything before `<!--more-->` is what the schedule shows,
so keep the list below it. `_sessions/2026/en/1-prerecorded.md` is a working example.

Links work too: `[text](https://example.ca)`.

## Editing one session by hand

The generator only touches rows in the spreadsheet, so editing the Markdown directly is fine for a
one-off change. Apply rules 1 and 2: change both languages, and keep `ref` matching the filename.

Each session is two files with the same name:

```
_sessions/2025/en/1-rds.md
_sessions/2025/fr/1-rds.md
```

The filename becomes the address: `_sessions/2025/en/1-rds.md` is published at
`https://dli-training.github.io/2025/en/1-rds/`.

Only `title`, `lang` and the description differ between the two. Everything else — `date`, `hour`,
`weight`, `ref`, `archive`, `category`, links — must match exactly.

## Session fields

| Field | What it does |
| --- | --- |
| `title` | Heading and schedule link text. Quote it: titles contain `\|`, `:` and apostrophes, which are meaningful in YAML. |
| `date` | `YYYY-MM-DD`. Groups sessions under a date heading. |
| `hour` | Start time beside the title. Include the timezone. |
| `weight` | Sort order within the day, lower first. Written by the generator from `hour`; you do not set it in the spreadsheet. |
| `lang` | `en` or `fr`. |
| `ref` | Links the EN and FR versions. Must equal the filename without `.md`. |
| `category` | Must be `presentation` to appear on the schedule and for the language toggle to work. |
| `archive` | The year, unquoted (`2025`, never `"2025"`). Sets which schedule and archive page list it. |
| `presenter` | A bracketed list: `[Name (Institution), Name (Institution)]`. |
| `slides` | One URL, or a list. Listed as *Document #1*, *#2*, … |
| `youtube_link` | Adds a "Watch on YouTube" button. |
| `room` / `location` | In-person location, and a URL for it. Shown only if `room` is set. |
| `session_link` | Zoom URL. Not displayed: the "JOIN ZOOM SESSION" button is commented out in `_layouts/session.html`. Uncomment it for a live event. |

Labels such as "Presented by:" and "Watch on YouTube" are translated once in `_data/menus.yml`, not
in the session files.

### How a session reaches the schedule

The Schedule page (`en/program.md`) and each year's archive page (`2025/en/2025.md`) declare what
they want:

```yaml
category: presentation
archive: 2025
```

The page lists every session whose `lang`, `category` **and** `archive` match its own, grouped by
`date` and ordered by `weight`. Nothing is listed by hand.

You do not fill in `weight`. The generator works out each day's order from `hour` and writes it,
so the running order follows the times you already entered. Two sessions at the same time keep the
order their rows appear in the spreadsheet. To force a different order, add a `weight` column and
set it on those rows; anything you put there is used as-is.

## Common tasks

### Update the committee contact list

The members list is plain Markdown at the bottom of `en/contact.md` and `fr/contact.md`. Email
addresses in angle brackets become links:

```markdown
### Atlantic Region

Sam Read : <sread@stfx.ca>
Sandra Sawchuk : <sandra.sawchuk@msvu.ca>
```

End each name's line with two spaces. That forces a line break; without it Markdown runs the names
into one paragraph.

### Change the text on a page

The main pages are in `en/` and `fr/`:

| File | Page |
| --- | --- |
| `index.md` | Home |
| `program.md` | Schedule |
| `archive.md` | Event Archive — the year cards are generated |
| `resources.md` | Resources |
| `contact.md` | Contact |
| `register.md` | Registration |
| `feedback.md` | Feedback |
| `workshop.md` | Workshops |
| `call-in.md` | Call-in details |
| `local.md` | Local information |
| `bio.md` | Presenter bios |
| `404.md` | Page-not-found |

Several contain blocks wrapped in `<!-- ... -->`, which hides them from visitors while keeping the
text in the file. To bring a block back, delete the `<!--` before it and the `-->` after it. To
retire one, wrap it the same way rather than deleting it.

`en/program.md` contains nested and unclosed comment markers. If text there appears or disappears
unexpectedly, look for a stray `<!--`.

### Add slides or recordings after the event

Fill in the `slides` and `youtube_link` columns and commit. Leave the description cells blank to
keep the existing session text.

By hand, edit both language files:

```yaml
slides: https://docs.google.com/presentation/d/FILE_ID/edit
youtube_link: https://youtu.be/VIDEO_ID
```

Set Google Drive sharing to allow anyone with the link to view.

### Where session content appears

The Schedule and each year's archive page use `_layouts/sessions.html`, which lists sessions as an
agenda: time, title, presenters, and the description down to `<!--more-->`. **Recording** and
**Materials** tags appear on any session with a `youtube_link` or `slides`.

An individual session page uses `_layouts/session.html`: date and time, title, presenters, the
recording as a button with any materials beside it, then the full description.

Styling is in `_sass/components/_schedule.scss` and `_sass/pages/sessions/_page-sessions-single.scss`.

### The Event Archive page

The page builds one card per training year from the session files, newest first, with the number of
sessions in each. A new year appears as soon as its sessions exist.

Text typed in the body of `en/archive.md` or `fr/archive.md` appears above the cards. The template
is `_layouts/archive.html` and the styling `_sass/components/_archive-cards.scss`.

### Update the date box on the home page

The dates and registration button come from `_data/contact.yml`. The box is currently switched off:
it sits inside a `<!--- ... --->` comment in `_layouts/home.html`. Remove those markers to show it.

### Change the contact email

Edit `email:` in `_config.yml`, which feeds the "Email us!" link.

> After editing `_config.yml`, stop and restart a local preview. Jekyll does not reload that file.
> This does not affect GitHub Pages.



## Previewing on your own computer

Needed only for larger changes. Requires [Ruby](https://www.ruby-lang.org/) and Git.

```bash
git clone git@github.com:dli-training/dli-training.github.io.git
cd dli-training.github.io
bundle install
bundle exec jekyll serve --livereload
```

Open <http://localhost:4000>. Pages rebuild as you save, except `_config.yml`, which needs a
restart.

The build prints Sass deprecation warnings from the bundled Bootstrap. Ignore them; the build
succeeded if it ends with `done in N seconds`.

Do not commit `_site/`. It is generated output and is already in `.gitignore`.

## Troubleshooting

**My change isn't on the live site.**
Wait two minutes and hard-refresh. Check the **Actions** tab for a failed build, and confirm you
committed to `master`.

**The spreadsheet Action failed.**
Open the run under **Actions** and read the error; it names the line and column. Nothing was
written. Fix the CSV and commit again. Usual causes: a date that isn't `YYYY-MM-DD`, an `hour` that
doesn't start with a 24-hour time, two rows sharing a `ref` in the same year, or an empty required
cell.

**The sessions are in the wrong order on a day.**
Order comes from `hour`, so check the times. A session written as `9:00` rather than `09:00` is
rejected for this reason.

**A session appears twice, or an old one won't go away.**
You renamed a `ref` and the old files are still there. The generator lists them as orphans; delete
the files it names.

**A new session isn't on the schedule.**
Check `category: presentation`; `archive:` matching the schedule page's `archive:` and unquoted;
`lang:` matching the page you are viewing; `date:` in `YYYY-MM-DD` form.

**The EN/FR toggle gives a 404.**
The twin file is missing, or its `ref:` does not match the filename. See rule 2.

**A page shows raw text, or the layout collapses.**
Front matter is broken. Check that both `---` lines are present, that there are no tabs, and that
any value containing a colon is wrapped in double quotes.

**Text I wrote isn't appearing.**
It is probably inside an HTML comment. Search the file for `<!--`.

**The whole build fails after my edit.**
A YAML error in `_config.yml` or `_data/` stops the build. Open the commit on GitHub, click
**Revert**, then reapply the change more carefully.

## Where everything lives

```
├── _config.yml          Site title, email, current_year
├── _data/
│   ├── sessions.csv     The programme — one row per session
│   ├── menus.yml        Navigation, footer, and session page labels
│   └── contact.yml      Home page date box and registration button
├── _scripts/
│   └── generate_sessions.py   Turns sessions.csv into session pages
├── .github/workflows/
│   └── generate-sessions.yml  Runs that script when the CSV changes
├── _sessions/           Session content, by year then language
├── 2020/ … 2025/        One archive landing page per year, per language
├── en/, fr/             The main pages
├── _layouts/            Page templates
├── _includes/           Reused fragments (header, breadcrumbs, menus, dates)
├── _sass/               Styles, including bundled Bootstrap
├── assets/              CSS, JavaScript, fonts
├── images/              Logos and illustrations
└── _site/               Generated output — never edited, never committed
```

Files and folders starting with `_` belong to Jekyll and are not published as pages.

---

## Credits

- Beautiful royalty free Illustrations by Icons8 - https://icons8.com/illustrations/style--pixeltrue
