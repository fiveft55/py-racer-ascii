# Dustline — Python ASCII Racer

A terminal motorcycle racer inspired by classic road combat games. Ride 5 km
through seeded, winding grasslands, deserts, pine forests, and badlands. Dodge
traffic, punch rival riders, and protect your bike: the shoulder slows you down
and damages your ride.

## Play

Requires Python 3.10+ and a Linux/macOS terminal with at least **72 × 24** cells.
No external packages are needed on Linux/macOS.

```sh
python3 racer.py
python3 racer.py --seed 42
```

On Windows, install `windows-curses` with `py -m pip install windows-curses`,
then run `py racer.py` in a compatible terminal. Windows has not been tested.

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
