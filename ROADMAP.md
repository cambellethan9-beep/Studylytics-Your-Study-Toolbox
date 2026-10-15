# Studylytics: Status Board and Roadmap

## Shipped

**Core**
- [x] Retro-styled home screen with tool tiles, a scrollable dashboard, and a daily study tip
- [x] Subject tabs that scope all data, with add, clear, and delete (two-step confirmation)
- [x] Local SQLite storage with automatic upgrades of older databases
- [x] In-app **? FAQ** button and a [FAQ](FAQ.md) covering dependencies, install steps, and what each tool is for
- [x] Linux launcher (`install_launcher.sh`), app icon, and `python3` shebang
- [x] SQL safety: every database query uses parameterized statements, so notepad text (or any other input) is never executed as SQL. The only string-built statement is an internal schema check on hard-coded table names.

**Tools**
- [x] Study Timer: live timer, session history, per-task stats, per-task time goals
- [x] Scheduler: auto-scheduled spaced-repetition reviews, month calendar with red "!" badges, editable intervals
- [x] Dedicate a timer session to a scheduled review (no duplicate entries)
- [x] Notes: per-subject notepad with two-keyword concept linking (15 lines above and below) or single-keyword highlighting, font size, underline, and clickable hyperlinks (Ctrl+click)
- [x] Notes: inline images with right-click resizing, and a full-screen draw tool with colors, text, undo, and a transparent page (images and drawing require Pillow)
- [x] Notes version history: automatic snapshots, preview, and one-click restore (30 versions per subject)
- [x] Mistake Log: missed questions become daily home-screen flashcards (right: gone, wrong: back tomorrow)
- [x] Pace Tracker: daily goal per subject, progress bar, all-time "you've studied X hours" total
- [x] Fast-Tab: saved links per subject, open them all with one click, optional time logging per link, and optional auto-stop when the window closes (needs `wmctrl` and X11)
- [x] "Still studying?" prompt for timed links that rely on a manual stop
- [x] To-do sidebar: per-subject, reorderable, collapsible task list that starts hidden
- [x] Daily study tips: 15 learning-science tips with a "Read more" explanation

## In progress

- Preparing the first public release (final testing and documentation).

## Planned: larger features

- [ ] **Command cheat sheet**
  - User-created categories, with commands added manually (typed from memory or pasted from research)
  - Global find across all categories: searching "switchport" returns every command containing it, from every category

## Future ideas (exploratory)

- [ ] **Study-effectiveness insights.** Log a 1-10 "how did that session feel" rating with each session, then analyze logs and ratings to spot patterns (for example, whether 1-hour sessions consistently beat 5-hour sessions) and make recommendations. Starting with plain statistics is likely enough before considering anything ML-based; it could all run locally.
- [ ] **More study tips.** The daily tip list is meant to keep growing with future updates.

## Known limitations / backlog

- [ ] Review intervals are global, not per subject
- [ ] Task names match exactly, so near-duplicates ("Flashcards" vs "flashcards") count as separate tasks outside the dedicated-review dropdown
- [ ] No overdue indicator for reviews from past days
- [ ] Fast-Tab auto-stop isn't available on Wayland (including default GNOME), because `wmctrl` only works on X11. Manual stop and the "Still studying?" prompt work everywhere.
- [ ] Saved Fast-Tab links can't be edited (remove and re-add instead)
- [ ] "Open all links" opens sites without starting any timers
- [ ] The "Still studying?" prompt covers Fast-Tab sessions only, not the Study Timer tab's own timer
- [ ] Non-Linux packaging (Windows/macOS) is not set up yet, and the app hasn't been tested there
