# Studylytics: Feature List

A retro-styled, all-in-one study toolbox built with Python. The core app uses only the standard library (`tkinter` + `sqlite3`), so there is nothing to install beyond Python and tkinter.

Two optional dependencies unlock specific features. Without them everything else works normally, and the affected controls are replaced by a short note:

- **Pillow**: inserting images and the draw tool in Notes.
- **wmctrl** (on an X11 session): Fast-Tab auto-stop.

See [FAQ.md](FAQ.md) for what each one is for and how to install it.

## Core app

- **Retro look and feel**: warm cream palette, monospace fonts, hand-drawn 8x8 pixel-art tool icons (drawn in code, no image assets needed for the UI).
- **Home screen with tool tiles**: a clickable tile for each tool (Study Timer, Scheduler, Notes, Mistake Log, Pace Tracker, Fast-Tab) with hover highlighting and a "< MENU" button on every tool page.
- **Scrollable home screen** (mouse wheel supported) so the dashboard sections always fit.
- **Local persistence**: all data is stored in a single SQLite file (`study_data.db`) created automatically on first run. Nothing is sent anywhere, and no account is needed.
- **Automatic schema migration**: older databases are upgraded in place. Pre-subject data is moved into a starter "General" subject, the goals table is rebuilt with a composite key, and existing notes gain history support.
- **Custom window/taskbar icon** loaded from `studylytics_icon.png` when present.
- **? FAQ button** in the top bar, visible on every page, which opens the FAQ on GitHub.
- **Safe on close**: closing the app saves your notes and logs any Fast-Tab sessions that are still running.

## Home dashboard

- **Today's goal**: a progress bar for the active subject's daily study goal.
- **Today's reviews**: scheduler items due today as checkboxes that disappear when checked (and mark the review complete).
- **Mistakes to review**: your Mistake Log flashcards for today (see Mistake Log).
- **Daily study tip**: see Daily study tips.

## Subjects (top tab bar)

- Persistent tab bar across every page. Switching subjects rescopes everything: Timer, Scheduler, Notes, Mistake Log, Pace Tracker, Fast-Tab links, the to-do sidebar, and the home dashboard.
- **"+ SUBJECT"** creates a new tab, then prompts for an optional daily study goal in hours (skippable, settable later in Pace Tracker).
- **"clear"** on each tab opens a dialog asking whether to also delete the tab, followed by a second "are you sure, this can't be undone" confirmation before anything is removed.
- Clearing removes that subject's sessions, task goals, scheduled reviews, notes and note history, mistake cards, daily goal, to-do items, and Fast-Tab links.
- The last remaining tab can't be deleted (its data can still be cleared).

## Study Timer

Four tabs: **Timer**, **History**, **Stats**, **Settings**.

- **Live start/stop timer** (HH:MM:SS) with a task dropdown that remembers previously used task names, or accepts a new one.
- **Session logging**: stopping the timer records the task, start time, stop time, and duration.
- **"Dedicate this session to a scheduled review"** dropdown lists today's due reviews. Picking one locks the task name to match exactly and checks that review off when you stop the timer, which avoids duplicate or mismatched entries.
- **History tab**: table of every logged session, newest first. Sessions timed through Fast-Tab appear here too.
- **Stats tab**: per-task total minutes, session count, average minutes per session, and progress toward any goal you set.
- **Settings tab**: set and delete allotted-time goals (in minutes) per task.

## Scheduler (spaced repetition)

- **Auto-scheduling**: the first time you log a session for a new task (from the Timer or from a Fast-Tab link), reviews are created at each configured interval, counted from that day. Later sessions for the same task do not reschedule it.
- **Month calendar** (weeks start on Sunday) with previous/next month navigation.
  - Today is highlighted teal, the selected day rust orange.
  - Days with reviews still due show a **bold red "!" badge**.
  - Days where every review is done show a subtle "." marker.
- **Day detail panel**: click any day to see its reviews and check or uncheck them.
- **Interval settings**: add or delete review intervals (days after initial learning). Defaults are 1, 3, 7, 14, and 30 days. Intervals are shared across all subjects.

## Notes (concept linker + rich text)

- Per-subject notepad for pasting study notes, with a scrollbar and undo.

**Highlighting**
- **Keyword linking**: enter two keywords and click "Highlight links". For every occurrence of keyword 1, the 15 lines above and below are searched for keyword 2. If found, everything from one keyword to the other (in either order) is highlighted in gold.
- If keyword 2 appears several times nearby, the closest occurrence to that keyword 1 hit is used.
- **Single-keyword mode**: leave keyword 2 blank to instead highlight every occurrence of keyword 1 on its own, so you can quickly scan everything nearby it.
- Matching is case-insensitive. "Clear highlights" removes the highlighting without touching the text.

**Formatting and links**
- **Font size** (8-24) and **underline**, applied to selected text from the toolbar.
- **Hyperlinks**: "Insert link" adds a clickable reference, either on the text you selected or with text you type. Links are blue and underlined, and **Ctrl+click** opens them in your browser (a plain click just places the cursor, so editing never launches a browser by accident).

**Images and drawing** *(require Pillow)*
- **Insert image**: PNG, JPG, GIF, or BMP, embedded inline and shown at up to 480px wide by default.
- **Resize in place**: right-click an image for Bigger (+20%), Smaller (-20%), Reset size, or Remove image. Resizing always starts from the original full-resolution image, so repeated resizing doesn't blur it, and your chosen size is saved.
- **Draw tool**: opens a large drawing window that fills the screen it opens on, with a 7-color palette, adjustable pen size (1-16), an **Add text** tool, **Undo** (up to 25 steps), and **Clear**.
- Drawings have a **transparent page**, so only your strokes and text are saved and the note's background shows through seamlessly. "Insert drawing" embeds the result inline.

**Version history**
- A **History** button next to "Save notes" lists earlier saved versions with their time and size, previews each, and restores the one you pick.
- A version is kept when there is none yet, when the previous version is at least 10 minutes old, or when a save loses a lot of text (200+ characters, or about 30% of it), which covers accidental deletions.
- The most recent 30 versions per subject are kept. Restoring keeps your current notes in history too, so it can be undone. Images show as `[image]` in the preview but are restored with the version.

**Saving**
- Formatting, links, images, and highlights are all saved and restored, not just the plain text. Notes saved before these features existed still load correctly.
- **Autosave** on: Save button, running a highlight, returning to the menu, switching subject tabs, and closing the app.

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

## Fast-Tab (saved links, optional time logging)

- **Saved links per subject**: add a label and a URL (`https://` is added if you leave it off). Each link has **Open** and **Remove** buttons.
- **Open all links** opens every saved site for the subject in your browser. It only opens them and does not start any timers.
- **Log time for this link** (optional, per link): clicking **Open** also starts a timer for the current subject, using the link's label as the task. The session is logged like any Study Timer session, and a new task gets its reviews scheduled automatically.
- **Stop button**: appears next to a link while it's being timed, and logs the session.
- **Auto-stop** (optional, per link; needs `wmctrl` on an X11 session): enter text from the site's window title, and the timer stops by itself once no open window contains it. Window titles are checked every 3 seconds, matching is case-insensitive, and if the window never shows up within 60 seconds, auto-stop gives up and leaves the timer for you to stop.
- **System check at startup**: Studylytics actually runs `wmctrl` to see whether window detection works. If it's missing, or installed but unable to read windows (typical on Wayland), auto-stop is disabled with a note explaining why, and links fall back to manual stop.
- **"Still studying?" prompt**: when a timed link relies on you to stop it and you come back to Studylytics after at least 10 seconds away, or touch it after about 2 minutes without activity, a small prompt asks whether to stop each one ("Stop & log") or keep going. This works on Wayland too, since it only watches Studylytics' own window.

## To-do sidebar

- A persistent sidebar on the right edge of every page, for miscellaneous tasks or a personal schedule that is separate from spaced-repetition reviews. For example: "configure DHCP in a Packet Tracer lab, then run a DHCP exhaustion attack from an end host."
- **Per subject**: each tab has its own list.
- Add items with the entry box (Enter or "+"). Check items off (they're struck through and stay until cleared), reorder them with the up/down arrows, delete them with the X, or use **Clear completed**.
- **Starts collapsed** as a thin strip on the right edge. Click the arrow or the "T-O-D-O" label to open it, and the arrow again to hide it. It scrolls independently of whichever page is showing.

## Daily study tips

- The home screen shows one study tip a day, drawn from 15 tips based on learning science (for example spaced repetition, retrieval practice, and interleaving). The list will grow over time.
- Each tip shows a short summary, and **Read more** opens the full explanation: what it is, the science behind it, and how it applies to studying.
- The tip changes once per day, not every time you open the app.

## Packaging (Linux)

- `#!/usr/bin/env python3` shebang so the script can run directly.
- `install_launcher.sh` creates a `.desktop` launcher (with icon) in your application menu so the app can be pinned to a dock or taskbar and started with a click. It optionally copies a launcher to `~/Desktop`.
- Update workflow: overwrite `studylytics.py` in place. The launcher and your data are unaffected.

## Safety

- Every database query uses parameterized statements, so text from notes or any other input is never executed as SQL. The only string-built statement is an internal schema check on hard-coded table names.

## Database tables

`subjects`, `sessions`, `goals` (task goals), `scheduled_reviews`, `review_intervals`, `notes`, `notes_history`, `subject_goals` (daily goals), `mistakes`, `todo_items`, `fast_links`.

## Known limitations

- Review intervals are global, not per subject.
- Task names are matched exactly, so near-duplicates ("Flashcards" vs "flashcards") count as separate tasks outside the dedicated-review dropdown.
- No overdue indicator for reviews from past days.
- Fast-Tab auto-stop needs `wmctrl` and an X11 session. It isn't available on Wayland (the default on many current desktops, including GNOME), where only manual stop and the "Still studying?" prompt work.
- Saved Fast-Tab links can't be edited. Remove and re-add them to change a setting.
- "Open all links" doesn't start timers. Use a link's own Open button for that.
- The "Still studying?" prompt covers Fast-Tab sessions only, not the Study Timer tab's own timer.
- Linux only for now. Windows and macOS packaging isn't set up, and the app hasn't been tested there.
