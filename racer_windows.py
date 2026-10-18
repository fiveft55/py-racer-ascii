#!/usr/bin/env python3
"""Native Windows 10 console edition of Dustline. No external dependencies."""
import argparse
import os
import shutil
import sys
import time

from racer import Race, render


class WindowsScreen:
    bold = 0

    def __init__(self):
        self.rows = []

    @staticmethod
    def color_pair(index):
        return index

    def getmaxyx(self):
        size = shutil.get_terminal_size((80, 24))
        return size.lines, size.columns

    def erase(self):
        height, _ = self.getmaxyx()
        self.rows = [[] for _ in range(height)]

    def addnstr(self, y, x, text, count, color=0):
        self.rows[y].append((x, text[:count], color))

    def refresh(self):
        colors = {0: 0, 1: 32, 2: 37, 3: 31, 4: 33}
        output = ['\x1b[H']
        for y, row in enumerate(self.rows):
            output.append(f'\x1b[{y + 1};1H\x1b[0m\x1b[2K')
            for x, text, color in row:
                output.append(f'\x1b[{y + 1};{x + 1}H\x1b[{colors.get(color, 0)}m{text}')
        sys.stdout.write(''.join(output) + '\x1b[0m')
        sys.stdout.flush()


def play(seed):
    import ctypes
    from ctypes import wintypes
    import msvcrt

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetStdHandle.argtypes = [wintypes.DWORD]
    kernel.GetStdHandle.restype = wintypes.HANDLE
    kernel.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    handle = kernel.GetStdHandle(-11 & 0xffffffff)
    original = wintypes.DWORD()
    if not kernel.GetConsoleMode(handle, ctypes.byref(original)):
        raise OSError('Open the game in PowerShell, Command Prompt, or Windows Terminal.')
    if not kernel.SetConsoleMode(handle, original.value | 0x0004):
        raise OSError('This console needs Windows 10 ANSI terminal support.')
    screen = WindowsScreen()
    race, paused, held = Race(seed), False, {}
    previous = time.monotonic()
    sys.stdout.write('\x1b[?1049h\x1b[?25l\x1b[2J')
    try:
        while True:
            now = time.monotonic()
            punch = 0
            while msvcrt.kbhit():
                key = msvcrt.getwch()
                if key in ('\x00', '\xe0'):
                    key = {'H': 'w', 'P': 's', 'K': 'a', 'M': 'd'}.get(msvcrt.getwch(), '')
                key = key.lower()
                if key in ('q', '\x1b'):
                    return
                if key == 'p':
                    paused = not paused
                    held.clear()
                if key == 'r' and race.done:
                    race, paused, held = Race(seed), False, {}
                held[key] = now + .18
                if key in ('j', 'l'):
                    punch = -1 if key == 'j' else 1
            active = lambda key: held.get(key, 0) > now
            height, width = screen.getmaxyx()
            if not paused and height >= 24 and width >= 72:
                race.update(now - previous, active('w'), active('s'),
                            int(active('d')) - int(active('a')), punch)
            previous = now
            render(screen, race, paused)
            time.sleep(1 / 30)
    finally:
        sys.stdout.write('\x1b[0m\x1b[?25h\x1b[?1049l')
        sys.stdout.flush()
        kernel.SetConsoleMode(handle, original.value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=1)
    args = parser.parse_args()
    if os.name != 'nt':
        parser.exit(1, 'Use racer_unix.py on Linux/macOS. This edition requires Windows 10 or later.\n')
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        parser.exit(1, 'Run this edition in an interactive Windows terminal.\n')
    try:
        play(args.seed)
    except KeyboardInterrupt:
        pass
    except OSError as exc:
        parser.exit(1, f'{exc}\n')


if __name__ == '__main__':
    main()
