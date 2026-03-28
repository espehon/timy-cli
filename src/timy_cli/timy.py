
import math
import time
import sys
import argparse
import importlib.metadata
from os import name, get_terminal_size
from subprocess import run

from colorama import Fore, init
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
    def __init__(self, width=50, height=25, stretch_x=True):
        self.width = width
        self.height = height
        self.stretch_x = stretch_x
        self.canvas = [[' '] * width for _ in range(width)]

    def reset_canvas(self):
        self.canvas = [[' '] * self.width for _ in range(self.width)]

    def plot(self, t, r, sym='*'):
        if self.stretch_x:
            row = int((self.height - r * math.cos(t)) / 2)
        else:
            row = int(self.height - r * math.cos(t))
        col = int(self.height + r * math.sin(t))

        if 0 <= row < self.width and 0 <= col < self.width:
            self.canvas[row][col] = sym

    def draw(self):
        self.reset_canvas()
        now = time.localtime()
        h = now.tm_hour * 6.283 + now.tm_min / 9.549
        min_size = 0.02
        hr_size = 0.01
        hr_fmt = 12

        for i in range(999):
            self.plot(i/158.0, 24)
            self.plot(h, i * min_size, "▓")
            self.plot(h / hr_fmt, i * hr_size, "█")
            for q in range(12):
                self.plot(q / 1.91, 24 - i * 0.005, '•')

        rendered = '\n'.join(''.join(row) for row in self.canvas[:self.height])
        time_str = f"{now.tm_hour:02}:{now.tm_min:02}"
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


def cli():
    if args.countdown is not None:
        countdownTimer(args.countdown[0])
    else:
        clock = AnalogClock()
        clock.render(args._refresh)