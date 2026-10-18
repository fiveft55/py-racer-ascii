#!/usr/bin/env python3
"""Dustline: a dependency-free procedural terminal motorcycle racer."""
import argparse
import sys
try:
    import curses
except ImportError:
    curses = None
from dataclasses import dataclass
import math
import random
import time


@dataclass
class Vehicle:
    distance: float
    lane: float
    speed: float
    rival: bool = False


class Race:
    finish = 5000

    def __init__(self, seed=1):
        self.seed = seed
        self.rng = random.Random(seed)
        self.distance = 0.0
        self.speed = 0.0
        self.lane = 0.0
        self.health = 100.0
        self.elapsed = 0.0
        self.cooldown = 0.0
        self.message = 'Reach 5 km. Stay on the asphalt!'
        self.vehicles = []
        self.spawn_at = 100.0
        self.hits = 0

    @property
    def done(self):
        return self.health <= 0 or self.distance >= self.finish

    def road(self, distance):
        """Smooth seeded bends, deterministic at any world coordinate."""
        phase = self.seed * 0.731
        return (math.sin(distance / 320 + phase) * 0.55
                + math.sin(distance / 137 + phase * 2) * 0.22)

    def biome(self, distance):
        return ('GRASSLAND', 'DESERT', 'PINE FOREST', 'BADLANDS')[int(distance // 800) % 4]

    def update(self, dt, throttle=False, brake=False, steer=0, punch=0):
        if self.done:
            return
        dt = min(max(dt, 0), 0.1)
        self.elapsed += dt
        self.cooldown = max(0, self.cooldown - dt)
        self.speed = max(0, min(70, self.speed + (22 if throttle else -5) * dt - (45 * dt if brake else 0)))
        old = self.distance
        self.distance += self.speed * dt
        bend = self.road(self.distance) - self.road(old)
        self.lane += steer * dt * 1.8 - bend * self.speed * 0.035
        self.lane = max(-1.55, min(1.55, self.lane))
        if abs(self.lane) > 0.88:
            self.speed = max(0, self.speed - 30 * dt)
            self.health = max(0, self.health - 7 * dt)
            self.message = 'OFF ROAD! Steer back onto the asphalt.'
        if self.distance + 240 >= self.spawn_at:
            self.vehicles.append(Vehicle(self.distance + self.rng.uniform(180, 260),
                                         self.rng.uniform(-0.66, 0.66),
                                         self.rng.uniform(18, 42), self.rng.random() < 0.55))
            self.spawn_at = self.distance + 310
        for vehicle in self.vehicles[:]:
            before = vehicle.distance - old
            vehicle.distance += vehicle.speed * dt
            gap = vehicle.distance - self.distance
            if punch and vehicle.rival and -7 < gap < 14 and 0.12 < (vehicle.lane - self.lane) * punch < 0.65 and self.cooldown == 0:
                self.vehicles.remove(vehicle)
                self.hits += 1
                self.cooldown = 0.6
                self.message = 'Rival knocked off balance!'
                continue
            if min(before, gap) <= 4 and max(before, gap) >= -4 and abs(vehicle.lane - self.lane) < 0.24:
                self.health = max(0, self.health - 23)
                self.speed *= 0.45
                self.vehicles.remove(vehicle)
                self.message = 'CRASH! Watch the traffic.'
            elif gap < -30:
                self.vehicles.remove(vehicle)
        if self.distance >= self.finish:
            self.message = 'FINISH! You survived Dustline.'
        elif self.health <= 0:
            self.message = 'WRECKED! Your ride is over.'


def put(screen, y, x, text, color=0):
    height, width = screen.getmaxyx()
    if 0 <= y < height - 1 and x < width - 1:
        trim = max(0, -x)
        try:
            screen.addnstr(y, max(0, x), text[trim:], max(0, width - max(0, x) - 1), color)
        except curses.error:
            pass


def render(screen, race, paused):
    screen.erase()
    height, width = screen.getmaxyx()
    if height < 24 or width < 72:
        put(screen, 0, 0, 'Resize terminal to at least 72 columns x 24 rows. Q quits.')
        screen.refresh()
        return
    green = curses.color_pair(1)
    road_color = curses.color_pair(2)
    danger = curses.color_pair(3)
    gold = curses.color_pair(4)
    horizon, bottom = 7, height - 6
    put(screen, 0, 2, 'D U S T L I N E   /   PROCEDURAL ROAD WAR', gold | curses.A_BOLD)
    put(screen, 1, 2, f'{race.speed * 3.6:3.0f} km/h   BIKE {race.health:3.0f}%   {race.distance / 1000:.2f} / 5.00 km   TIME {race.elapsed:5.1f}s')
    put(screen, 2, 2, f'{race.biome(race.distance)}   SEED {race.seed}   TAKEDOWNS {race.hits}', green)
    put(screen, 4, width // 2 - 15, '    /\\       /\\    /\\       /\\ ', green)
    put(screen, 5, width // 2 - 20, r'___/  \_____/  \__/  \_____/  \___', green)
    view = bottom - horizon
    for y in range(horizon, bottom + 1):
        depth = (y - horizon + 1) / (view + 1)
        ahead = (1 - depth) ** 2 * 240
        center = width / 2 + (race.road(race.distance + ahead) - race.road(race.distance)) * width * 0.34
        half = 2 + depth * width * 0.33
        left, right = int(center - half), int(center + half)
        world = int((race.distance + ahead) / 9)
        terrain = '. ' if race.biome(race.distance + ahead) in ('DESERT', 'BADLANDS') else ', '
        put(screen, y, 0, (terrain * width)[:width - 1], green)
        put(screen, y, left, '|' + ' ' * max(0, right - left - 1) + '|', road_color)
        if world % 3:
            put(screen, y, int(center), ':', gold)
        if world % 7 == 0:
            put(screen, y, left - 4, 'Y' if terrain == ', ' else '*', green)
    for vehicle in sorted(race.vehicles, key=lambda v: v.distance, reverse=True):
        gap = vehicle.distance - race.distance
        if not 0 <= gap <= 240:
            continue
        depth = 1 - math.sqrt(gap / 240)
        y = horizon + int(depth * view)
        center = width / 2 + (race.road(vehicle.distance) - race.road(race.distance)) * width * 0.34
        x = int(center + vehicle.lane * (2 + depth * width * 0.33))
        put(screen, y, x - 1, 'o^o' if vehicle.rival else '[#]', danger)
    player_x = int(width / 2 + race.lane * (2 + width * 0.33))
    put(screen, bottom - 1, player_x, 'O', gold | curses.A_BOLD)
    put(screen, bottom, player_x - 1, '/A\\', gold | curses.A_BOLD)
    put(screen, height - 4, 2, race.message, danger if race.health < 30 else gold)
    put(screen, height - 3, 2, 'W/UP gas  S/DOWN brake  A/D or arrows steer  J/L punch  P pause  Q quit')
    if paused or race.done:
        put(screen, height - 2, 2, 'PAUSED - P resumes' if paused and not race.done else 'Race complete. R: race again   Q: quit', gold)
    screen.refresh()


def play(screen, seed):
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    screen.nodelay(True)
    screen.keypad(True)
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        for index, color in enumerate((curses.COLOR_GREEN, curses.COLOR_WHITE, curses.COLOR_RED, curses.COLOR_YELLOW), 1):
            curses.init_pair(index, color, -1)
    race = Race(seed)
    paused = False
    held = {}
    previous = time.monotonic()
    while True:
        now = time.monotonic()
        punch = 0
        while True:
            key = screen.getch()
            if key == -1:
                break
            if key in (ord('q'), ord('Q'), 27):
                return
            if key == ord('p'):
                paused = not paused
                held.clear()
            if key == ord('r') and race.done:
                race = Race(seed)
                paused = False
                held.clear()
            held[key] = now + 0.18
            if key in (ord('j'), ord('l')):
                punch = -1 if key == ord('j') else 1
        active = lambda keys: any(held.get(key, 0) > now for key in keys)
        height, width = screen.getmaxyx()
        if not paused and height >= 24 and width >= 72:
            race.update(now - previous, active((ord('w'), curses.KEY_UP)), active((ord('s'), curses.KEY_DOWN)),
                        int(active((ord('d'), curses.KEY_RIGHT))) - int(active((ord('a'), curses.KEY_LEFT))), punch)
        previous = now
        render(screen, race, paused)
        time.sleep(1 / 30)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=1, help='procedural course seed (default: 1)')
    args = parser.parse_args()
    if curses is None:
        parser.exit(1, 'Terminal support is missing. On Windows, run:\n'
                    '  py -m pip install -r requirements.txt\n'
                    'Then run: py racer.py\n')
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        parser.exit(1, 'Run this game in an interactive terminal (PowerShell, Command Prompt, or Windows Terminal).\n')
    try:
        curses.wrapper(play, args.seed)
    except KeyboardInterrupt:
        pass
    except curses.error as exc:
        parser.exit(1, f'Terminal initialization failed: {exc}\n'
                    'Use a terminal window at least 72 columns by 24 rows.\n')


if __name__ == '__main__':
    main()
