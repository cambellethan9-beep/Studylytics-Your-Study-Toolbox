# Studylytics

Studylytics is a retro-styled desktop toolbox that tracks your study time, schedules spaced-repetition reviews, and turns your practice-test mistakes into daily flashcards. Everything runs locally with nothing to install beyond Python.

<!-- Add a screenshot of the home screen here, e.g. ![Studylytics home screen](screenshot.png) -->

## Quick start

**Requirements:** Python 3 with `tkinter`. That's all the core app needs.

**Optional:** Pillow, only needed for two things in Notes (inserting images and the draw tool). Everything else works fine without it.

If tkinter is missing on Debian/Ubuntu:

```
sudo apt-get install python3-tk
```

**Installing Pillow (optional):** on Debian/Ubuntu, install it through your system's package manager rather than `pip` - newer versions block `pip` from touching system Python to avoid breaking OS tools (you'll see an "externally-managed-environment" error if you try `pip install` directly):

```
sudo apt install python3-pil python3-pil.imagetk
```

Both packages are needed - the second one is what lets Pillow images display inside tkinter, which Studylytics relies on. Confirm it worked with:

```
python3 -c "from PIL import Image, ImageTk; print('ok')"
```

**Run it:**

```
python3 studylytics.py
```

**Optional (Linux): add it to your app menu** so you can launch it with a click and pin it to your dock or taskbar. Keep `studylytics.py`, `studylytics_icon.png`, and `install_launcher.sh` in the same folder, then run:

```
chmod +x install_launcher.sh
./install_launcher.sh
```

## Learn more

- [How to use Studylytics](USAGE.md)
- [Full feature list](FEATURES.md)
- [Roadmap](ROADMAP.md)

## Your data

Everything is stored in `study_data.db`, created next to the script the first time you run it. To update the app, replace `studylytics.py` with the new version. Your data is not affected.
