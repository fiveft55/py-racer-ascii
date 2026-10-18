# How Dustline works — caveman edition

Big idea: **bike world has a brain. Terminal shows pictures. Keyboard gives orders.**
You do not need to understand everything at once. Read one piece, open the named
function, then come back here.

## 1. Where everything lives

| File | Caveman meaning | Actual job |
| --- | --- | --- |
| [`racer.py`](../racer.py) | World brain and drawing plan | Shared simulation, drawing rules, and original curses runner |
| [`racer_windows.py`](../racer_windows.py) | Windows hands and screen | Native Windows input and ANSI terminal output |
| [`racer_unix.py`](../racer_unix.py) | Linux/macOS front door | Calls the curses runner in `racer.py` |
| [`play.bat`](../play.bat) | Windows start button | Runs the Windows edition from its own folder |
| [`test_racer.py`](../test_racer.py) | Robot checks toy | Tests rules and drawing without playing a whole race |
| [`.github/workflows/tests.yml`](../.github/workflows/tests.yml) | Two robot caves | Configures GitHub tests on Linux and Windows |
| [`.gitignore`](../.gitignore) | Ignore this pile | Keeps generated Python files and virtual environments out of commits |

```text
Windows keys -> racer_windows.py --+
                                  +-> Race.update() -> world changes
Unix keys ---> racer_unix.py ------+                        |
                                                           v
                                                        render()
                                                           |
                                     platform screen <-----+
```

Both editions share the same game rules. They differ in how they read keys and
draw characters in a terminal. The Unix launcher is tiny because its terminal
backend still lives in `racer.py`.

## 2. Tiny Python dictionary

| Code | Meaning |
| --- | --- |
| `class Race:` | Describe what a race object contains and can do |
| `def update(...):` | Define a named action |
| `self` | This particular object |
| `self.speed` | The speed stored inside this object |
| `x = 5` | Store 5 in x |
| `x += 2` | Add 2 to the existing x |
| `if condition:` | Do the indented part only when the condition is true |
| `for vehicle in vehicles:` | Do something for each vehicle |
| `while True:` | Keep repeating until something stops the loop |
| `return` | Leave this function, optionally handing back a value |
| `import` | Bring in tools from another Python module |

Indentation is part of Python's grammar. Indented lines belong to the block
above them.

## 3. Vehicle: one small information box

In `racer.py`, `Vehicle` uses `@dataclass`. Python creates the basic storage and
constructor for us. This makes a rival bike:

```python
Vehicle(distance=200, lane=-0.4, speed=30, rival=True)
```

Translation: **enemy bike, 200 metres along road, left side, moving at 30 metres
per second.** Distance is its world position, not its distance from you.

`lane` is a position across the road: negative means left, zero means middle,
positive means right. `rival=False` means ordinary traffic.

## 4. Race: the world in a box

`Race.__init__()` runs when we create `Race(seed)`. It sets the starting state:

```python
self.distance = 0.0
self.speed = 0.0
self.health = 100.0
```

**Bike stopped. Bike healthy. Journey just started.**

The object also remembers traffic, elapsed time, the random generator, your lane,
punch cooldown, and a message for the player. The `done` property checks whether
you have no health left or have reached the 5,000 metre finish.

## 5. update(): move the world one tiny step

The runner repeatedly calls:

```python
race.update(dt, throttle, brake, steer, punch)
```

`dt` is elapsed time in seconds since the last frame. Speed is measured internally
in metres per second. The display multiplies it by 3.6 to show km/h.

```python
self.distance += self.speed * dt
```

At 20 metres per second, half a second adds 10 metres. The game caps each update
at 0.1 seconds so a long delay cannot cause one enormous simulation jump.

Each update roughly does this:

1. Stop immediately if the race is already over.
2. Advance the clock and reduce the punch cooldown.
3. Accelerate, coast, or brake.
4. Move forward, apply steering, and apply drift caused by road bends.
5. Slow and damage the bike when it leaves the asphalt.
6. Spawn traffic ahead when needed.
7. Move vehicles and check punches, collisions, and vehicles left behind.
8. Set the finish or wreck message.

The road bends can push you outward harder at speed. There is no full motorcycle
physics engine; these are deliberately simple rules.

## 6. Procedural road: smooth snake maths

`road(distance)` answers: **how far does the road bend at this world position?**
It combines two `math.sin()` waves. A sine wave smoothly moves back and forth:

```text
left -> middle -> right -> middle -> left
```

Mix two waves with different lengths and the bends feel less repetitive. The
seed changes their phase, which means where the waves start in their cycle.
The same seed reproduces the same road.

```powershell
py -3 racer_windows.py --seed 42
```

The seed also initializes a private random generator for traffic. Traffic
placement depends on when you travel forward and spawn vehicles, so a different
riding pace can change the traffic you encounter even on the same road.

`biome(distance)` is simpler: every 800 metres it selects the next landscape:

```text
grassland -> desert -> pine forest -> badlands -> repeat
```

The `%` operator wraps the list index back to the beginning. There is no giant
map file: the game calculates the road and scenery as it needs them.

## 7. Crashes and punches: compare positions

For each vehicle, the simulation finds its distance relative to you:

```python
gap = vehicle.distance - self.distance
```

Positive gap: ahead of you. Negative gap: behind you.

A collision checks whether your longitudinal positions overlap closely during
the step and whether your lanes are close enough. A crash removes health, cuts
your speed, and removes that vehicle. The shoulder damages you gradually instead.

Punching requires a rival nearby, on the side you punched, slightly ahead or
alongside, with no active cooldown. A successful punch removes the rival and
increments `hits`, which the HUD displays as takedowns. Ordinary cars cannot be
punched away.

## 8. render(): fake depth with text

There is no 3D graphics engine. `render()` draws a narrow road near the horizon
and a wide road near your bike:

```text
          | |
         |   |
        |     |
       |       |
      |   /A\   |
```

**Far narrow. Near wide. Brain sees depth.**

For each screen row, the renderer calculates how far ahead it represents. It
samples the road at that distance to find the bend, then draws terrain, road
edges, and markings. Nearby objects appear lower on the screen. Distant objects
appear higher. Vehicles are drawn from farthest to nearest.

| Symbol | Meaning |
| --- | --- |
| `/A\` | Your motorcycle |
| `o^o` | Rival rider |
| `[#]` | Car |
| `:` | Centre road marking |
| `Y` / `*` | Roadside scenery |

`put()` clips text to the terminal bounds. This helps prevent drawing errors
near an edge. A terminal smaller than 72 columns by 24 rows gets a resize notice,
and the runner pauses world updates until there is room again.

## 9. Windows edition: native input and ANSI output

`racer_windows.py` imports the shared `Race` and `render()` functions.

- `msvcrt.kbhit()` asks whether a key is waiting.
- `msvcrt.getwch()` reads a key without waiting for Enter.
- Arrow keys arrive as special sequences; the runner maps them to W/A/S/D.
- `ctypes` calls Windows console functions to enable ANSI output.
- `WindowsScreen` translates shared drawing instructions into ANSI commands.

An ANSI command is text with a special prefix. The terminal interprets it as an
instruction rather than showing it literally. For example, `\x1b[H` moves the
cursor to the top-left. Other commands move to a row/column or change colour.

`WindowsScreen.erase()` starts a new frame buffer. `addnstr()` stores a drawing
operation. `refresh()` sends the accumulated operations to the terminal.

The runner saves the original console mode. Its `finally` block restores that
mode and the visible cursor when the loop exits, including after Ctrl+C.

No `windows-curses` package is needed for this edition. Importing the shared
module tolerates missing curses, and the Windows screen supplies its own colours.
Actual Windows keyboard and console behaviour still needs testing on Windows;
Linux tests can check the output adapter but cannot prove all Windows API calls.

## 10. Unix edition: curses does the terminal work

`racer_unix.py` imports `main()` from `racer.py` and calls it when launched:

```python
if __name__ == '__main__':
    main()
```

This means **start when run directly; do not automatically start when imported.**

`main()` reads `--seed`, checks terminal support, and calls `curses.wrapper()`.
The wrapper prepares the terminal, calls `play()`, and restores terminal settings
when it exits. Curses provides keyboard input, cursor movement, and colours.

## 11. The game loop: repeat until quit

Both runners follow this pattern:

```text
Read keys
    |
    v
Update world, unless paused or terminal too small
    |
    v
Draw frame
    |
    v
Wait about 1/30 second
    |
    +------> start again
```

`time.monotonic()` measures elapsed time without depending on the wall clock.
The frame rate is roughly 30 FPS, with some extra time spent drawing each frame.

A key press is treated as active for 0.18 seconds. Repeated key events extend
that time. This imitates holding a key in terminals, which generally give key
press events rather than reliable key-release events. It also means movement
can feel different depending on your keyboard repeat settings.

P toggles pause. R creates a fresh `Race` after a finish or wreck. Q leaves the
loop. J/L punches are triggered by key events.

## 12. Other files: launching, testing, and Git

`play.bat` moves into its own folder and runs `py -3 racer_windows.py`. `%*`
forwards extra arguments, so `play.bat --seed 42` works too. On an error, `pause`
keeps the window open so you can read the message.

`test_racer.py` sets up small situations and checks the results. For example:
put a car on the player, advance time, then check that health fell. It also checks
seeded roads, acceleration, traffic, punches, race completion, and rendering.
Mock objects stand in for a real screen, so tests do not require interactive play.

The GitHub workflow is configured to run those tests and launcher help commands
on Linux and Windows with Python 3.12. Configuration alone does not establish
that a particular remote CI run passed. The help commands do not launch a race.

`.gitignore` keeps `__pycache__`, compiled Python files, and `.venv` out of normal
Git additions. The README contains the quick-start commands.

## 13. Read the code in this order

1. `Vehicle`: what one vehicle remembers.
2. `Race.__init__()`: what a race remembers at the start.
3. `Race.update()`: how those values change.
4. `road()` and `biome()`: how the world is generated.
5. `render()` and `put()`: how the world becomes text.
6. Your platform's `play()`: how keys, updates, and drawing connect.
7. `main()`: how launching the program starts everything.

For a first experiment, change `Race.finish` from `5000` to `1000` and play a
shorter race. Change one thing at a time, then run the tests. Their job is to
warn you when a change breaks an existing rule.
