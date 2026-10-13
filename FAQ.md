# Studylytics FAQ

- [What do I need to install?](#what-do-i-need-to-install)
- [How do I install each dependency?](#how-do-i-install-each-dependency)
- [Dependency troubleshooting](#dependency-troubleshooting)
- [What is each tool for, and how does it help me study?](#what-is-each-tool-for-and-how-does-it-help-me-study)
- [How the tools fit together](#how-the-tools-fit-together)
- [Data, backups, and updating](#data-backups-and-updating)

---

## What do I need to install?

Studylytics is built on Python's standard library, so most of it works with nothing beyond Python itself. A few optional extras unlock specific features.

| If you want to use... | You need | Required? |
| --- | --- | --- |
| Everything except the items below: timer, scheduler, mistake log, pace tracker, to-do list, note text, highlighting, links, Fast-Tab links | Python 3 with **tkinter** | **Yes** |
| **Insert image** and the **Draw** tool in Notes | **Pillow** (with its tkinter support) | Optional |
| Fast-Tab **auto-stop** (timer stops when a window closes) | **wmctrl**, on an **X11** session | Optional |
| Links opening from Fast-Tab, Notes, and the FAQ button | Any web browser (your system default is used) | Yes, for links |

You don't need an internet connection or an account. Everything is stored locally. The internet is only used when you open a link.

If you skip an optional dependency, Studylytics still runs. The features that need it are replaced by a short note explaining what to install.

---

## How do I install each dependency?

The commands below are for Debian and Ubuntu-based systems, which is what Studylytics has been tested on. Fedora and Arch commands use the usual package names but haven't been tested.

### Python 3 and tkinter (required)

```
sudo apt install python3 python3-tk
```

Fedora: `sudo dnf install python3 python3-tkinter`
Arch: `sudo pacman -S python tk`

Check that it worked:

```
python3 -c "import tkinter; print('tkinter ok')"
```

### Pillow (optional: images and drawing in Notes)

Install it through your system's package manager, not `pip`. Newer Debian and Ubuntu releases block `pip` from changing system Python.

```
sudo apt install python3-pil python3-pil.imagetk
```

Both packages are needed. The second one lets Pillow images display inside tkinter.

Fedora: `sudo dnf install python3-pillow python3-pillow-tk`
Arch: `sudo pacman -S python-pillow`

Check that it worked:

```
python3 -c "from PIL import Image, ImageTk; print('Pillow ok')"
```

Restart Studylytics afterward.

### wmctrl (optional: Fast-Tab auto-stop)

```
sudo apt install wmctrl
```

Fedora: `sudo dnf install wmctrl`
Arch: `sudo pacman -S wmctrl`

`wmctrl` only works on **X11** sessions. On **Wayland**, which is the default on many current desktops including GNOME, it can't see other windows, so auto-stop isn't available no matter what you install. To check which session you're on:

```
echo $XDG_SESSION_TYPE
```

If it prints `wayland`, auto-stop won't work. The rest of Fast-Tab still does, including manual **Stop** and the "Still studying?" prompt.

Studylytics checks for `wmctrl` once at startup, so restart it after installing.

### Windows and macOS

Studylytics is developed and tested on Linux. It's plain Python, so it may run elsewhere, but that hasn't been tested. tkinter comes with the installers from python.org. Pillow can be installed with `pip install Pillow`. `wmctrl` and the Linux launcher script (`install_launcher.sh`) are Linux-only, so Fast-Tab auto-stop won't be available.

---

## Dependency troubleshooting

**`ModuleNotFoundError: No module named 'tkinter'`**
tkinter isn't installed. Install it with the commands above.

**`error: externally-managed-environment` when I run `pip`**
Your system protects its Python from `pip`. Use the `apt` packages above instead. Avoid `--break-system-packages`, since it can break system tools.

**I don't see "Insert image" or "Draw" in Notes.**
Pillow, or its tkinter support (`python3-pil.imagetk`), isn't installed. Notes shows a note about this in place of those buttons. Install both packages and restart.

**The Fast-Tab auto-stop checkbox is greyed out.**
Either `wmctrl` isn't installed, or it's installed but can't read windows, which usually means a Wayland session. A note below the checkbox says which. Restart Studylytics after installing.

---

## What is each tool for, and how does it help me study?

### Subject tabs (top bar)

**What it does:** Each tab (for example "Security+" or "CCNA") is a separate workspace. Your timer sessions, reviews, notes, mistakes, goals, links, and to-do list all belong to whichever tab is active. **+ SUBJECT** adds one, and **clear** on a tab wipes its data when you're finished with it, such as after passing an exam.

**How it helps:** Subjects stay separate, so one doesn't clutter another. When you finish a certification, you can clear it without touching anything else.

### Study Timer

**What it does:** Start and stop a timer for a task. Each session is logged. **History** lists every session, **Stats** shows total time, session count, and average session length per task, and **Settings** lets you set a time goal per task.

**How it helps:** It makes the time you actually spend visible. People often misjudge which topics get the most attention. Stats shows where your hours went, so you can spot what you've been neglecting and rebalance.

### Scheduler (spaced repetition)

**What it does:** The first time you log a new task, Studylytics schedules reviews of it at increasing intervals, **1, 3, 7, 14, and 30 days** later by default. You can add or remove intervals in the Scheduler's Settings. A month calendar shows what's due (a red **!** marks days with reviews left), and today's reviews appear on the home screen as a checklist. In the Timer, you can dedicate a session to a due review so it's checked off.

**How it helps:** Memory fades quickly after you learn something, then more slowly each time you review. Reviewing just as you're about to forget is one of the best-supported ways to keep material long-term, and it works better than cramming. The Scheduler does the planning, so you don't have to remember when to revisit things.

### Notes

**What it does:** A notepad for each subject.
- **Concept linking:** enter two keywords, and wherever the second shows up within 15 lines of the first, the text between them is highlighted. Leave the second blank to highlight every occurrence of the first.
- **Formatting:** font sizes and underline.
- **Hyperlinks:** **Insert link** adds a clickable reference. Ctrl+click opens it.
- **Images and drawing** *(needs Pillow)*: insert pictures, or draw with a color palette, pen sizes, text, and undo. Right-click an image to make it bigger or smaller, reset it, or remove it.
- **History:** restore an earlier version of your notes if you delete something by accident.

**How it helps:** Related ideas are easier to remember when you can see how they connect, and the highlighting shows which concepts sit near each other in your notes. Pairing words with diagrams gives you two ways to recall the same idea. History means a bad edit doesn't cost you hours of work.

### Mistake Log

**What it does:** After a practice test, log each question you missed along with its correct answer. Cards due today appear on the home screen one at a time. Click **Show answer**, then **Got it right** or **Got it wrong**. A card you get right is removed for good. A card you get wrong comes back tomorrow.

**How it helps:** Trying to recall an answer before you see it strengthens memory far more than rereading does. Because only the questions you missed come back, and they keep coming back until you get them right, your review time goes to your weakest spots.

### Pace Tracker

**What it does:** Set a daily study goal in minutes for each subject. It shows a progress bar for today and your all-time total, for example "You've studied 42 hours on Network+!" The same progress bar appears on the home screen.

**How it helps:** A small daily target is easier to keep up than a vague plan to study a lot. Because each subject has its own goal, one subject can't quietly use up the time meant for another. The running total shows progress already made instead of a deadline.

### Hyperlink Fast-Tab

**What it does:** Save the sites you open every time you study, such as a video playlist or a reference page. **Open all links** opens every saved site for the subject at once. It only opens them and doesn't start any timers. For a single link, **Open** opens it, and if you enabled **Log time for this link**, it also starts timing, using the link's label as the task. You can stop with the **Stop** button. If Fast-Tab auto-stop is available on your system (it needs `wmctrl` and an X11 session), the timer stops by itself when the window closes. Either way, if you come back to Studylytics while a link is still being timed, a **"Still studying?"** prompt asks whether to stop.

**How it helps:** Setting up a study session is friction, and friction makes it easier to put things off. Opening your usual sites in one click removes that, and timing a link means the time gets logged without you remembering to start a timer.

### To-do sidebar

**What it does:** A per-subject checklist on the right edge of every screen, for tasks that aren't review sessions. For example: "Configure DHCP in Packet Tracer, then run a DHCP exhaustion attack from an end host." Items can be reordered, checked off, deleted, or cleared in bulk once completed. It starts collapsed. Click **«** or the **T-O-D-O** strip to open it.

**How it helps:** Keeping tasks in your head takes up mental space you want for studying. Writing them down, and breaking a big lab into ordered steps, frees that space and keeps you from losing track of what's next.

### Daily study tip

**What it does:** The home screen shows one study tip a day, based on learning science, and **Read more** opens the full explanation. The tip changes once a day, not every time you open the app.

**How it helps:** It builds your understanding of why these methods work, which makes it easier to use them well.

---

## How the tools fit together

A typical session might look like this:

1. **Open Studylytics.** The home screen shows today's progress, reviews that are due, and mistake cards waiting for you.
2. **Do your reviews and flashcards.** Check off due reviews and answer your mistake cards.
3. **Open your usual sites** with Fast-Tab.
4. **Study with the timer running.** Take notes, link related concepts, and add diagrams.
5. **Log new mistakes** after any practice test, so they return as flashcards.
6. **Check your pace.** See whether you hit today's goal for each subject.

Logging a new task in the timer also schedules its future reviews automatically, so the Scheduler fills itself in as you study.

---

## Data, backups, and updating

**Where is my data stored?** In a single file named `study_data.db`, created next to `studylytics.py` the first time you run it. To back up everything, copy that file. If you delete it, Studylytics starts fresh.

**How do I update?** Replace `studylytics.py` with the new version. Your data isn't affected.
