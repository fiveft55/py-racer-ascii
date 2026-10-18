# Dustline — Python ASCII Racer

A terminal motorcycle racer inspired by classic road combat games. Ride 5 km
through seeded, winding grasslands, deserts, pine forests, and badlands. Dodge
traffic, punch rival riders, and protect your bike: the shoulder slows you down
and damages your ride.

## Play

Requires Python 3.10+ and a terminal with at least **72 × 24** cells.
No external packages are needed on Linux/macOS.

```sh
python3 racer.py
python3 racer.py --seed 42
```

### Windows 10 (PowerShell or Command Prompt)

Install **64-bit Python 3.12** from python.org (enable the Python launcher during
installation), then download/extract or clone this repository. Open PowerShell
or Command Prompt in the project folder and run:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe racer.py
```

After setup, run **`play.bat`** from the project folder (or double-click it).
It uses the local virtual environment, so PowerShell script activation and
execution-policy changes are unnecessary. Windows Terminal is recommended;
PowerShell and Command Prompt in the standard Windows console also work with
`windows-curses`. Use a window at least 72 columns wide and 24 rows tall.
Run in a terminal, rather than IDLE, an editor output panel, or redirected output.

If `py` is unavailable, reinstall Python with the launcher enabled, or substitute
`python` for `py -3.12` above after confirming `python --version` is 3.10 or newer.
If pip reports no matching `windows-curses` wheel, use 64-bit Python 3.12 as above.

The included Windows CI workflow runs the simulation and renderer smoke tests. Interactive Windows
keyboard/display behavior still needs a manual check on a Windows machine.

| Key | Action |
| --- | --- |
| W / Up | Accelerate (hold) |
| S / Down | Brake (hold) |
| A / D or Left / Right | Steer (hold) |
| J / L | Punch a nearby rival on your left / right |
| P | Pause / resume |
| R | Restart after finishing or wrecking |
| Q / Escape | Quit |

Your rider is `/A\`; rival bikes are `o^o` and cars are `[#]`. Bends pull the
bike outward at speed. Punch when a rival is alongside and slightly ahead.
Terminal input uses key repeat, so short taps steer gently and held keys repeat
after your terminal's initial delay. Resizing below the minimum pauses simulation.
The same seed reproduces the road; traffic depends on your pace.

## Development

```sh
python3 -m unittest -v
```

`racer.py` contains a standalone simulation (`Race`) and a curses renderer.
Tests exercise seeded generation, traffic, acceleration, damage, combat, and race
completion without requiring a terminal. No assets, services, or credentials are
required.
