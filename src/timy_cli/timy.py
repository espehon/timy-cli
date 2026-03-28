
import math
import time
import sys
import argparse
import importlib.metadata
from datetime import datetime
from os import name, get_terminal_size
from subprocess import run

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from colorama import Fore, init
from timy_cli.settings import load_or_create_settings

init(autoreset=True)


# Set __version__
try:
    __version__ = f"timy {importlib.metadata.version('timy-cli')}"
except importlib.metadata.PackageNotFoundError:
    __version__ = "Package not installed..."


parser = argparse.ArgumentParser(description='Print an analog clock to the consol!', add_help=False)

parser.add_argument('-?', '--help', action='help', help='Show this help message and exit.')

parser.add_argument('-v', '--version', action='version', version='%(prog)s {version}'.format(version=__version__))

parser.add_argument('-l', '--live', dest='_refresh', action='store_true', help='Refresh every minute until stopped. (live clock)')

parser.add_argument('-s', '--stopwatch', action='store_true', help='Interactive Stopwatch timer')

parser.add_argument('-c', '--countdown', metavar='M', action='append', type=int, nargs='?', const=60, help='Countdown timer for [M] minutes (default 60)')

parser.add_argument('-m', '--multiple', action='store_true', help='Show multiple timezones (defined in settings.json)')

args = parser.parse_args() #Execute parse_args()




def clear():
    if name == 'nt':
        _ = run('cls', shell=True)
    else:
        _ = run('clear')


def load_zone(zone_name):
    if zone_name is None:
        return None
    if isinstance(zone_name, str) and zone_name.lower() == 'local':
        return None
    try:
        return ZoneInfo(zone_name)
    except Exception:
        normalized = zone_name.replace(' ', '_') if isinstance(zone_name, str) else zone_name
        try:
            return ZoneInfo(normalized)
        except Exception:
            return None


def zone_label(zone_name):
    if zone_name is None:
        return 'Unknown'
    if isinstance(zone_name, str) and zone_name.lower() == 'local':
        return 'Local'
    return zone_name


def countdownTimer(Minutes):
    clear()
    paddingWithGlass = get_terminal_size()[1] - 32 # 32 is length of the following outputs
    if paddingWithGlass > 0:
        print("\n" * paddingWithGlass)
    print('''
         _.-"""-._
    _.-""         ""-._
  :"-.               .-":
  '"-_"-._       _.-".-"'
    ||T+._"-._.-"_.-"|
    ||:   "-.|.-" : ||
    || .   ' ||  .  ||
    ||  .   '|| .   ||
    ||   ';.:||'    ||
    ||    '::||     ||
    ||      :||     ||
    ||     ':||     ||
    ||   .' :||.    ||
    ||  ' . :||.'   ||
    ||.'-  .:|| -'._||
  .-'": .::::||:. : "'-.
  :"-.'::::::||::'  .-":
   "-."-._"--:"  .-".-"
      "-._"-._.-".-"
          "-.|.-"
               ''')
    try:
        for m in progressbar(range(Minutes), prefix="Timer: " +str(Minutes) + " Min ", suffix="(pass ← wait)"):
            time.sleep(60)
            if m == Minutes - 1:
                clear()
                print("\n" * get_terminal_size()[1])
        print(f'''{Fore.LIGHTGREEN_EX}
        +====+
        |(  )|
        | )( |
        |(::)|
        +====+
    Timer has ended!''')
        print("\a")
    except:
        print(f"\n\n{Fore.YELLOW}[Timer interrupted]\n\n")
        

def progressbar(it, prefix="", suffix=""): #progressbar -->  prefix: [############################.............................] i/it
    size = abs(get_terminal_size()[0] - len(prefix) - len(suffix) - 16)
    count = len(it)
    def show(j):
        x = int(size*j/count)
        sys.stdout.write("%s[%s%s] %i ← %i %s  \r" % (prefix, "#"*x, "."*(size-x), j, (count-j), suffix))
        sys.stdout.flush()
    show(0) #This prints the progressbar at 0 progress. Then next for loop renders the rest (stating at 1)
    for i, item in enumerate(it): #This is the 'i' in the comment on the 'def' line
        yield item
        show(i+1)
    sys.stdout.write("\n")
    sys.stdout.flush()


class AnalogClock:
    def __init__(self, width=None, height=25, stretch_x=True, zone_name=None):
        self.height = height
        self.stretch_x = stretch_x
        self.zone_name = zone_name
        self.timezone = load_zone(zone_name)
        self.width = width if width is not None else (height * 2 if stretch_x else height)
        self.canvas = [[' '] * self.width for _ in range(self.height)]
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.x_radius = self.width // 2 - 1
        self.y_radius = self.height // 2 - 1
        self.x_scale = self.x_radius / 24.0
        self.y_scale = self.y_radius / 24.0

    def reset_canvas(self):
        self.canvas = [[' '] * self.width for _ in range(self.height)]

    def plot(self, t, r, sym='*'):
        row = int(self.center_y - r * self.y_scale * math.cos(t))
        col = int(self.center_x + r * self.x_scale * math.sin(t))

        if 0 <= row < self.height and 0 <= col < self.width:
            self.canvas[row][col] = sym

    def current_time(self):
        if self.timezone is None:
            return datetime.now().astimezone()
        return datetime.now(self.timezone)

    def draw(self):
        self.reset_canvas()
        now = self.current_time()
        h = now.hour * 6.283 + now.minute / 9.549
        min_size = 0.02
        hr_size = 0.01
        hr_fmt = 12

        for i in range(999):
            self.plot(i / 158.0, 24)
            self.plot(h, i * min_size, "▓")
            self.plot(h / hr_fmt, i * hr_size, "█")
            for q in range(12):
                self.plot(q / 1.91, 24 - i * 0.005, '•')

        rendered = '\n'.join(''.join(row) for row in self.canvas)
        time_str = now.strftime("%H:%M")
        return rendered, time_str

    def render(self, refresh=False):
        try:
            while True:
                print('\n' * 4)
                rendered, time_str = self.draw()
                print(rendered)
                print(" " * int(((self.width / 2) - 2)) + time_str)
                if refresh:
                    print("\n[ctrl + c] to terminate", end='')
                    time.sleep(60)
                    clear()
                else:
                    break
        except KeyboardInterrupt:
            return


class SmallClock:
    def __init__(self, zone_name=None, stretch_x=False):
        self.zone_name = zone_name
        self.timezone = load_zone(zone_name)
        self.stretch_x = stretch_x
        self.base_width = 13
        self.height = 9
        self.width = self.base_width * 2 if stretch_x else self.base_width
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.radius = min(self.center_x, self.center_y) - 1

    def current_time(self):
        if self.timezone is None:
            return datetime.now().astimezone()
        return datetime.now(self.timezone)

    def hand_position(self, step, radius):
        angle = step * (math.pi / 6)
        row = int(round(self.center_y - math.cos(angle) * radius))
        col = int(round(self.center_x + math.sin(angle) * radius))
        return row, col

    def draw(self):
        now = self.current_time()
        canvas = [[' '] * self.width for _ in range(self.height)]

        for tick in range(12):
            row, col = self.hand_position(tick, self.radius)
            if 0 <= row < self.height and 0 <= col < self.width:
                canvas[row][col] = '.'

        # Center marker
        if 0 <= self.center_y < self.height and 0 <= self.center_x < self.width:
            canvas[self.center_y][self.center_x] = '+'

        minute_step = round(now.minute / 5) % 12
        hour_total = (now.hour % 12) * 12 + now.minute // 5
        hour_step = round(hour_total / 12) % 12

        hour_row, hour_col = self.hand_position(hour_step, self.radius - 2)
        minute_row, minute_col = self.hand_position(minute_step, self.radius - 1)

        if 0 <= hour_row < self.height and 0 <= hour_col < self.width:
            canvas[hour_row][hour_col] = 'h'
        if 0 <= minute_row < self.height and 0 <= minute_col < self.width:
            if (minute_row, minute_col) == (hour_row, hour_col):
                canvas[minute_row][minute_col] = 'X'
            else:
                canvas[minute_row][minute_col] = 'm'

        rendered = '\n'.join(''.join(row) for row in canvas)
        time_str = now.strftime("%H:%M")
        return rendered, time_str


class MultipleClockRenderer:
    def __init__(self, zone_names, stretch_x=False, padding=4):
        self.zone_names = [zone for zone in zone_names if zone is not None][:4]
        if not self.zone_names:
            self.zone_names = ['local']
        self.padding_string = ' ' * padding
        self.clocks = [SmallClock(zone_name=zone, stretch_x=stretch_x) for zone in self.zone_names]

    def render_once(self):
        rendered_clocks = [clock.draw() for clock in self.clocks]
        clock_lines = [rendered.splitlines() for rendered, _ in rendered_clocks]
        widths = [len(lines[0]) for lines in clock_lines]

        top_labels = [zone_label(zone)[:width].center(width) for zone, width in zip(self.zone_names, widths)]
        bottom_labels = [time_str.center(width) for (_, time_str), width in zip(rendered_clocks, widths)]

        composed = [self.padding_string.join(top_labels)]
        for row in range(len(clock_lines[0])):
            composed.append(self.padding_string.join(lines[row] for lines in clock_lines))
        composed.append(self.padding_string.join(bottom_labels))
        return '\n'.join(composed)

    def render(self, refresh=False):
        try:
            while True:
                print('\n' * 4)
                print(self.render_once())
                if refresh:
                    print("\n[ctrl + c] to terminate", end='')
                    time.sleep(60)
                    clear()
                else:
                    break
        except KeyboardInterrupt:
            return


def cli():
    if args.countdown is not None:
        countdownTimer(args.countdown[0])
    elif args.multiple:
        settings = load_or_create_settings()
        zones = [settings.get(key) for key in [
            'TimeZone1',
            'TimeZone2',
            'TimeZone3',
            'TimeZone4',
        ] if settings.get(key) is not None][:4]
        stretch_x = settings.get('stretch_x', True)
        renderer = MultipleClockRenderer(zones, stretch_x=stretch_x)
        renderer.render(args._refresh)
    else:
        settings = load_or_create_settings()
        stretch_x = settings.get('stretch_x', True)
        main_zone = settings.get('MainZone', 'local')
        clock = AnalogClock(stretch_x=stretch_x, zone_name=main_zone)
        clock.render(args._refresh)