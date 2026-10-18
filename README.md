# Dustline — ASCII Motorcycle Racing

Race 5 km through seeded roads, grasslands, deserts, forests, and badlands.
Dodge traffic and punch rival riders. Crashes and riding off road damage your bike.

## Windows 10 edition

Install Python 3.10+ from python.org with the Python launcher enabled. Download
and extract this project, then double-click **play.bat**, or open PowerShell or
Command Prompt in the project folder and run:

```powershell
py -3 racer_windows.py
py -3 racer_windows.py --seed 42
```

This edition uses native Windows console input and ANSI rendering. **No pip
packages, virtual environment, or windows-curses installation is needed.**
Windows Terminal, PowerShell, or Command Prompt on Windows 10 are supported
terminal targets. Interactive Windows operation still requires manual verification;
the development environment is Linux.

## Linux / macOS edition

Uses Python's standard-library curses support. Run:

```sh
python3 racer_unix.py
python3 racer_unix.py --seed 42
```

Both editions require Python 3.10+ and a terminal of at least **72 × 24** cells.
Keep `racer.py` beside both launchers: it contains the shared game simulation
and drawing rules. The two editions have separate terminal input/output backends.
`racer.py` also remains usable as the original curses entry point.

## Controls

| Key | Action |
| --- | --- |
| W / Up | Accelerate |
| S / Down | Brake |
| A / D or Left / Right | Steer |
| J / L | Punch left / right |
| P | Pause / resume |
| R | Restart after finishing or wrecking |
| Q / Escape | Quit |

Your bike is `/A\`, rivals are `o^o`, and cars are `[#]`. Punch a rival alongside
and slightly ahead of you. Bends pull your bike outward at speed. Held keys use
terminal key repeat; short taps give fine steering. Resizing below the minimum
pauses the race. Run in a terminal, rather than IDLE or an editor output panel.

## Tests

```sh
python3 -m unittest -v
```

On Windows, use `py -3 -m unittest -v`. CI is configured for Linux and Windows.
