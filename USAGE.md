# How to Use Studylytics

New here? The [FAQ](FAQ.md) explains what to install and what each tool is for. This page walks through using them.

## The basics

- The **home screen** has a tile for each tool. Click a tile to open it, and use **< MENU** to come back.
- The **tab bar at the very top** is your list of subjects (for example "CCNA" or "Security+"). Everything in the app, including your timer, reviews, notes, mistakes, goals, links, and to-do list, belongs to whichever subject tab is active. Switching tabs switches all of it.
- The **home screen dashboard** shows, for the active subject: today's study goal progress, reviews due today, mistake flashcards to review, and a study tip of the day.
- The **to-do sidebar** sits on the right edge of every page (see section 8). It starts collapsed.
- **? FAQ** in the top bar opens the FAQ on GitHub.

## 1. Set up a subject

1. Click **+ SUBJECT** in the top bar and name it (for example "Security+").
2. Enter a daily study goal in hours, or leave it blank to skip. You can set it later in Pace Tracker.
3. Click the tab to switch to it. A starter tab called "General" already exists, and you can use it or ignore it.

## 2. Log your study time (Study Timer)

1. Open **Study Timer** and stay on the **Timer** tab.
2. Type what you're studying (for example "Subnetting") or pick a previous task from the dropdown.
3. Click **START**. Click **STOP** when you're done. The session is saved.

Check your sessions under **History**, your totals and averages under **Stats**, and set a time goal for a specific task under **Settings**.

## 3. Reviews happen automatically (Scheduler)

The first time you log a **new** task, Studylytics schedules review sessions for it at increasing intervals (by default 1, 3, 7, 14, and 30 days later). This also happens when a Fast-Tab link you're timing logs a new task.

- **Home screen:** anything due today appears under "Today's reviews" as a checkbox. Check it and it disappears.
- **Scheduler tile:** a month calendar. Days with reviews still due show a red **!**. Click a day to see and check off its reviews.
- **Scheduler > Settings:** add or remove intervals (for example add a 2-day review).
- **Reviewing during a timed session:** on the Timer tab, use the "Dedicate this session to a scheduled review" dropdown to pick today's review. It locks the task name and checks the review off when you stop the timer.

## 4. Notes

Open **Notes** and paste or type your study notes. They save automatically when you leave the page, switch subjects, or close the app.

**Link related concepts**
1. Enter two related terms, for example `WPA2` and `CCMP`.
2. Click **Highlight links**. Wherever the second term appears within 15 lines of the first, everything between them is highlighted in gold.
3. Leave the second term blank to highlight every occurrence of the first term instead.

Highlighting is not case-sensitive. **Clear highlights** removes it without changing your text.

**Format text**
- Select text, choose a size, and click **Apply**, or click **U (underline)**.

**Add links to references**
1. Optionally select the text you want to turn into a link.
2. Click **Insert link** and enter the web address. If nothing was selected, you'll also be asked what text to show.
3. **Ctrl+click** a link to open it. A plain click just places your cursor.

**Add images and drawings** *(need Pillow, see the [FAQ](FAQ.md))*
- **Insert image** picks a PNG, JPG, GIF, or BMP file and places it where your cursor is.
- **Draw** opens a large drawing window. Pick a color and pen size and draw. Click **Add text** and then click on the canvas to place text. Use **Undo** to step back and **Clear** to start over. Click **Insert drawing** to place it in your note. Only your strokes and text are kept, so the drawing blends into the page.
- **Right-click an image** to make it bigger or smaller, reset its size, or remove it.

**Recover earlier versions**
- Click **History** (next to Save notes) to see earlier versions of your notes. Select one to preview it, then click **Restore this version**. Your current notes are kept in history too, so you can switch back.

## 5. Mistake Log (flashcards from what you got wrong)

1. After a practice test, open **Mistake Log** and enter each missed question and its correct answer.
2. On the **home screen**, the "Mistakes to review" section shows one card at a time. Click **Show answer**, then:
   - **Got it right:** the card is gone for good.
   - **Got it wrong:** it comes back tomorrow.

## 6. Pace Tracker

Open **Pace Tracker** to set your daily goal for the active subject (in minutes) and see today's progress as a percentage bar. It also shows your all-time total for that subject. The home screen shows the same progress bar, so you can see at a glance whether you've hit your goal.

## 7. Fast-Tab (open your usual sites in one click)

1. Open **FAST-TAB**.
2. Under **Add a site**, enter a label (for example "Network+ video playlist") and the web address. You can leave off `https://`.
3. Optional: check **Log time for this link**. Clicking **Open** will then also start a timer for the current subject, using the label as the task.
4. Click **Add link**. Your saved links appear under **Your links**.

Using your links:
- **Open** opens that site. If it's set to log time, the timer starts, and a **Stop** button appears next to it. Click **Stop** when you're done, and the session is logged.
- **Open all links** opens every saved site for the subject. It only opens them and doesn't start any timers.
- **Remove** deletes a link. Links can't be edited, so remove and re-add one to change it.
- If you leave a timed link running and come back to Studylytics later, a **"Still studying?"** prompt asks whether to stop it or keep going.

**Optional auto-stop:** if you check **Auto-stop by detecting the window closing**, you can enter a word or phrase from that site's window title (for example `FREE CCNA`), and the timer stops on its own when the window closes. This needs `wmctrl` and an X11 session. On Wayland (the default on many desktops, including GNOME) it isn't available, and the page tells you so. Manual **Stop** and the "Still studying?" prompt still work. The [FAQ](FAQ.md) has the details.

## 8. To-do sidebar

The sidebar starts collapsed as a thin strip on the right edge.

1. Click the **«** arrow (or the **T-O-D-O** label) to open it. Click **»** to hide it again.
2. Type a task in the box and press **Enter** or click **+**.
3. Check a task off when it's done. It's struck through but stays in the list.
4. Use the **up and down arrows** to reorder, the **X** to delete one, and **Clear completed** to remove everything checked off.

Each subject tab has its own list, and it's separate from your Scheduler reviews. It's a good place for things like lab steps ("configure DHCP in Packet Tracer, then run an exhaustion attack from an end host").

## 9. Finishing a subject

Done with a subject, like after passing an exam? Click **clear** on its tab.

1. Choose whether to also delete the tab.
2. Confirm the second prompt.

That subject's sessions, reviews, notes (and their history), mistakes, goals, links, and to-do items are removed, and your other subjects are untouched. You can't delete your last remaining tab, but you can still clear its data.
