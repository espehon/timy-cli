
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
from questionary import Choice
import questionary
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

parser.add_argument('-z', '--zone', action='store_true', help='Configure timezone settings interactively')

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


POPULAR_ZONES = [
    ('UTC', 'UTC'),
    ('US Eastern (New York)', 'America/New_York'),
    ('US Central (Chicago)', 'America/Chicago'),
    ('US Mountain (Denver)', 'America/Denver'),
    ('US Pacific (Los Angeles)', 'America/Los_Angeles'),
    ('Arizona (no DST)', 'America/Phoenix'),
    ('Hawaii (no DST)', 'Pacific/Honolulu'),
    ('Alaska', 'America/Anchorage'),
    ('London', 'Europe/London'),
    ('Central Europe (Berlin)', 'Europe/Berlin'),
    ('Eastern Europe (Athens)', 'Europe/Athens'),
    ('Moscow', 'Europe/Moscow'),
    ('India (Kolkata)', 'Asia/Kolkata'),
    ('China (Shanghai)', 'Asia/Shanghai'),
    ('Japan (Tokyo)', 'Asia/Tokyo'),
    ('Singapore', 'Asia/Singapore'),
    ('Australia Eastern (Sydney)', 'Australia/Sydney'),
    ('Australia Central (Darwin, no DST)', 'Australia/Darwin'),
    ('Australia Western (Perth, no DST)', 'Australia/Perth'),
    ('New Zealand (Auckland)', 'Pacific/Auckland'),
]

ZONE_CANCELLED = '__cancelled__'


def zone_choices(include_disabled=False):
    choices = [Choice('Local', 'local')]
    if include_disabled:
        choices.append(Choice('Disabled', '__disabled__'))
    choices.extend(Choice(label, value) for label, value in POPULAR_ZONES)
    choices.append(Choice('More', '__more__'))
    return choices


def choose_zone(current_zone, include_disabled=False):
    selected = questionary.select(
        'Select a timezone:',
        choices=zone_choices(include_disabled),
        default=current_zone,
    ).ask()
    if selected is None:
        return ZONE_CANCELLED
    if selected == '__disabled__':
        return None
    if selected != '__more__':
        return selected

    try:
        from zoneinfo import available_timezones
    except ImportError:
        from backports.zoneinfo import available_timezones

    all_zones = sorted(available_timezones())

    return questionary.select(
        'Select a timezone from the full list:',
        choices=[Choice('Local', 'local')] + [Choice(zone, zone) for zone in all_zones],
        default=current_zone if current_zone in all_zones else None,
    ).ask() or ZONE_CANCELLED


def configure_zones():
    from timy_cli.settings import save_settings

    settings = load_or_create_settings()
    target = questionary.select(
        'Which timezone setting do you want to change?',
        choices=[
            Choice('Main clock', 'MainZone'),
            Choice('Multi clock 1', 'TimeZone1'),
            Choice('Multi clock 2', 'TimeZone2'),
            Choice('Multi clock 3', 'TimeZone3'),
            Choice('Multi clock 4', 'TimeZone4'),
            Choice('Done', '__done__'),
        ],
    ).ask()

    while target not in (None, '__done__'):
        selected_zone = choose_zone(settings.get(target), target != 'MainZone')
        if selected_zone == ZONE_CANCELLED:
            return
        settings[target] = selected_zone
        save_settings(settings)
        print(f"{target} set to {settings[target] or 'disabled'}")
        target = questionary.select(
            'Choose another setting:',
            choices=[
                Choice('Main clock', 'MainZone'),
                Choice('Multi clock 1', 'TimeZone1'),
                Choice('Multi clock 2', 'TimeZone2'),
                Choice('Multi clock 3', 'TimeZone3'),
                Choice('Multi clock 4', 'TimeZone4'),
                Choice('Done', '__done__'),
            ],
        ).ask()


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
                print(zone_label(self.zone_name).center(self.width))
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
        self.height = 11
        self.width = self.base_width * 2 if stretch_x else self.base_width
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.radius = self.center_y - 1
        self.x_scale = 2 if stretch_x else 1

    def current_time(self):
        if self.timezone is None:
            return datetime.now().astimezone()
        return datetime.now(self.timezone)

    def hand_position(self, step, radius):
        angle = step * (math.pi / 6)
        row = int(round(self.center_y - math.cos(angle) * radius))
        col = int(round(self.center_x + math.sin(angle) * radius * self.x_scale))
        return row, col

    def draw_line(self, canvas, step, radius, symbol):
        end_row, end_col = self.hand_position(step, radius)
        for distance in range(1, radius + 1):
            fraction = distance / radius
            row = int(round(self.center_y + (end_row - self.center_y) * fraction))
            col = int(round(self.center_x + (end_col - self.center_x) * fraction))
            if 0 <= row < self.height and 0 <= col < self.width:
                canvas[row][col] = symbol

    def draw(self):
        now = self.current_time()
        canvas = [[' '] * self.width for _ in range(self.height)]

        for tick in range(12):
            row, col = self.hand_position(tick, self.radius)
            if 0 <= row < self.height and 0 <= col < self.width:
                canvas[row][col] = 'o'

        for label, step, offset in [('12', 0, -1), ('3', 3, 0), ('6', 6, 0), ('9', 9, 0)]:
            row, col = self.hand_position(step, self.radius)
            col += offset
            for index, character in enumerate(label):
                if 0 <= row < self.height and 0 <= col + index < self.width:
                    canvas[row][col + index] = character

        minute_step = round(now.minute / 5) % 12
        hour_step = round(((now.hour % 12) * 60 + now.minute) / 60) % 12
        self.draw_line(canvas, hour_step, self.radius - 2, 'H')
        self.draw_line(canvas, minute_step, self.radius - 1, 'M')

        if 0 <= self.center_y < self.height and 0 <= self.center_x < self.width:
            canvas[self.center_y][self.center_x] = '+'

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
    if args.zone:
        configure_zones()
    elif args.countdown is not None:
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