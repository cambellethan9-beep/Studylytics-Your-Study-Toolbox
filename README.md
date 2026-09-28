# Studylytics

Studylytics is a retro-styled desktop toolbox that tracks your study time, ...

<p align="center">
  <img src="studylytics_icon.png" alt="Studylytics icon" width="96">
</p>

## Quick start

**Requirements:** Python 3 with `tkinter` (no other packages needed).

If tkinter is missing on Debian/Ubuntu:

```
sudo apt-get install python3-tk
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
