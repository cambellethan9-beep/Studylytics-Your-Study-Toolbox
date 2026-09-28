# Studylytics: Status Board and Roadmap

## Shipped

- [x] Retro-styled home screen with tool tiles and a scrollable dashboard
- [x] Subject tabs that scope all data, with add, clear, and delete (two-step confirmation)
- [x] Study Timer: live timer, session history, per-task stats, per-task time goals
- [x] Scheduler: auto-scheduled spaced-repetition reviews, month calendar with red "!" badges, editable intervals
- [x] Dedicate a timer session to a scheduled review (no duplicate entries)
- [x] Notes: per-subject notepad with two-keyword concept linking (15 lines above and below) and gold highlighting
- [x] Mistake Log: missed questions become daily home-screen flashcards (right: gone, wrong: back tomorrow)
- [x] Pace Tracker: daily goal per subject, progress bar, all-time "you've studied X hours" total
- [x] Linux launcher (`install_launcher.sh`), app icon, and `python3` shebang
- [x] SQL safety: every database query uses parameterized statements, so notepad text (or any other input) is never executed as SQL. The only string-built statement is an internal schema check on hard-coded table names.

## In progress

- Nothing currently in progress.

## Planned: next up (smaller items)

- [ ] **Study-tip splash messages** at the bottom of the home screen, with rotating, useful study advice
- [ ] **FAQ link** to the GitHub FAQ page so users can view it from inside the app
- [ ] **Notes: single-keyword highlight.** If only one keyword is entered, highlight every occurrence of it so nearby context is easy to scan
- [ ] **Notes: formatting.** Adjustable font size and underlining
- [ ] **To-do sidebar.** A clean, fluid sidebar for miscellaneous tasks or a personal schedule that is separate from spaced-repetition reviews (example: "configure DHCP in a Packet Tracer lab, then run a DHCP exhaustion attack from an end host")

## Planned: larger features

- [ ] **Command cheat sheet**
  - User-created categories, with commands added manually (typed from memory or pasted from research)
  - Global find across all categories: searching "switchport" returns every command containing it, from every category
- [ ] **Notes: images and drawing**
  - Insert images into notes for diagrams and screenshots
  - Draw tool with multiple colors
  - Note: notes are currently stored as plain text, so this needs a richer storage format (images and formatting stored alongside the text)
- [ ] **Hyperlink Fast-Tab**
  - Save the sites you open every time you study, then open them all with one click
  - Optional: link a site to a subject's study timer so time is logged automatically while that site's window is open and stops when it closes
  - Note: detecting window open/close is OS-specific (X11 vs Wayland on Linux), so the first version may be a simpler start/stop-with-launch approach

## Future ideas (exploratory)

- [ ] **Study-effectiveness insights.** Log a 1-10 "how did that session feel" rating with each session, then analyze logs and ratings to spot patterns (for example, whether 1-hour sessions consistently beat 5-hour sessions) and make recommendations. Starting with plain statistics is likely enough before considering anything ML-based; it could all run locally.

## Known limitations / backlog

- [ ] Review intervals are global, not per subject
- [ ] Task names match exactly, so near-duplicates ("Flashcards" vs "flashcards") count as separate tasks outside the dedicated-review dropdown
- [ ] No overdue indicator for reviews from past days
- [ ] Non-Linux packaging (Windows/macOS) is not set up yet
