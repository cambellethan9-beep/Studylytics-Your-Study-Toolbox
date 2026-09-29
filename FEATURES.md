# Studylytics: Feature List

A retro-styled, all-in-one study toolbox built with Python. The core app uses only the standard library (`tkinter` + `sqlite3`), so there is nothing to `pip install`. Pillow is an optional dependency, needed only for inserting images and the draw tool in Notes; without it, everything else works normally and those two buttons are replaced with a short note.

## Core app

- **Retro look and feel**: warm cream palette, monospace fonts, hand-drawn 8x8 pixel-art tool icons (drawn in code, no image assets needed for the UI).
- **Home screen with tool tiles**: a clickable tile for each tool (Study Timer, Scheduler, Notes, Mistake Log, Pace Tracker) with hover highlighting and a "< MENU" button on every tool page.
- **Scrollable home screen** (mouse wheel supported) so the dashboard sections always fit.
- **Local persistence**: all data is stored in a single SQLite file (`study_data.db`) created automatically on first run.
- **Automatic schema migration**: older databases are upgraded in place. Pre-subject data is moved into a starter "General" subject, and the goals table is rebuilt with a composite key.
- **Custom window/taskbar icon** loaded from `studylytics_icon.png` when present.

## Subjects (top tab bar)

- Persistent tab bar across every page. Switching subjects rescopes everything below it (Timer, Scheduler, Notes, Mistake Log, Pace Tracker, home dashboard).
- **"+ SUBJECT"** creates a new tab, then prompts for an optional daily study goal in hours (skippable, settable later in Pace Tracker).
- **"clear"** on each tab opens a dialog asking whether to also delete the tab, followed by a second "are you sure, this can't be undone" confirmation before anything is removed.
- Clearing removes that subject's sessions, task goals, scheduled reviews, notes, mistake cards, and daily goal.
- The last remaining tab can't be deleted (its data can still be cleared).

## Study Timer

Four tabs: **Timer**, **History**, **Stats**, **Settings**.

- **Live start/stop timer** (HH:MM:SS) with a task dropdown that remembers previously used task names, or accepts a new one.
- **Session logging**: stopping the timer records the task, start time, stop time, and duration.
- **"Dedicate this session to a scheduled review"** dropdown lists today's due reviews. Picking one locks the task name to match exactly and checks that review off when you stop the timer, which avoids duplicate or mismatched entries.
- **History tab**: table of every logged session, newest first.
- **Stats tab**: per-task total minutes, session count, average minutes per session, and progress toward any goal you set.
- **Settings tab**: set and delete allotted-time goals (in minutes) per task.

## Scheduler (spaced repetition)

- **Auto-scheduling**: the first time you log a session for a new task, reviews are created at each configured interval, counted from that day. Later sessions for the same task do not reschedule it.
- **Month calendar** (weeks start on Sunday) with previous/next month navigation.
  - Today is highlighted teal, the selected day rust orange.
  - Days with reviews still due show a **bold red "!" badge**.
  - Days where every review is done show a subtle "." marker.
- **Day detail panel**: click any day to see its reviews and check or uncheck them.
- **Interval settings**: add or delete review intervals (days after initial learning). Defaults are 1, 3, 7, 14, and 30 days. Intervals are shared across all subjects.

## Notes (concept linker + rich text)

- Per-subject notepad for pasting study notes, with a scrollbar and undo.
- **Keyword linking**: enter two keywords and click "Highlight links". For every occurrence of keyword 1, the 15 lines above and below are searched for keyword 2. If found, everything from one keyword to the other (in either order) is highlighted in gold.
- If keyword 2 appears several times nearby, the closest occurrence to that keyword 1 hit is used.
- **Single-keyword mode**: leave keyword 2 blank to instead highlight every occurrence of keyword 1 on its own, so you can quickly scan everything nearby it.
- Matching is case-insensitive. "Clear highlights" removes the highlighting without touching the text.
- **Formatting**: select text and apply a font size (8-24) or toggle underline from the toolbar.
- **Images** *(requires Pillow)*: insert an image from a file, embedded inline and auto-resized if wider than 480px.
- **Draw tool** *(requires Pillow)*: a popup canvas with a 7-color palette and adjustable pen size; "Insert drawing" embeds the result inline.
- Formatting, images, and highlights are all saved and restored, not just the plain text. Notes saved before this feature existed still load correctly.
- **Autosave** on: Save button, running a scan, returning to the menu, switching subject tabs, and closing the app.

## Mistake Log

- Log a missed practice-test question and its correct answer (multi-line fields), per subject.
- Each new card is due immediately.
- **Daily flashcard review on the home screen**: one card at a time with a "N cards due" counter. Click "Show answer" to reveal it, then:
  - **Got it right**: the card is removed permanently.
  - **Got it wrong**: the card comes back tomorrow.
- Full table of all logged mistakes (question, answer, next due date) with delete.

## Pace Tracker

- Set a **daily study goal in minutes** per subject (also prompted at subject creation).
- **Progress bar and percentage** for today's logged time against the goal, per subject.
- A compact version of the same progress bar appears on the home screen.
- Positive framing: shows an all-time total such as **"YOU'VE STUDIED X HOURS ON [SUBJECT]!"** instead of a countdown.

## Home dashboard

- **Today's goal** progress bar for the active subject.
- **Today's reviews**: scheduler items due today as checkboxes that disappear when checked (and mark the review complete).
- **Mistake review card** (see Mistake Log).

## Packaging (Linux)

- `#!/usr/bin/env python3` shebang so the script can run directly.
- `install_launcher.sh` creates a `.desktop` launcher (with icon) in your application menu so the app can be pinned to a dock or taskbar and started with a click. It optionally copies a launcher to `~/Desktop`.
- Update workflow: overwrite `studylytics.py` in place. The launcher and your data are unaffected.

## Database tables

`subjects`, `sessions`, `goals` (task goals), `scheduled_reviews`, `review_intervals`, `notes`, `subject_goals` (daily goals), `mistakes`.

## Known limitations / ideas

- Review intervals are global, not per subject.
- Task names are matched exactly, so near-duplicates ("Flashcards" vs "flashcards") count as separate tasks outside the dedicated-review dropdown.
- No overdue indicator for reviews from past days.
- Planned: study-tip splash messages at the bottom of the home screen.
