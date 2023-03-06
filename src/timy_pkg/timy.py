
import math
import time
import sys
import argparse
import importlib.metadata
from os import system, name, get_terminal_size

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

parser.add_argument('-r', '--refresh', dest='_refresh', action='store_true', help='Refresh every minute until stopped')

parser.add_argument('-c', '--continuous', dest='_refresh', action='store_true', help='Alias for --refresh')

parser.add_argument('-t', '--timer', metavar='M', action='append', type=int, nargs='?', const=60, help='Countdown timer for [M] minutes (default 60)')

args = parser.parse_args() #Execute parse_args()




def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

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
        for m in progressbar(range(Minutes), prefix="Timer: " +str(Minutes) + " Min ", sufix="(pass ← wait)"):
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
        

def progressbar(it, prefix="", sufix=""): #progressbar -->  prefix: [############################.............................] i/it
    size = abs(get_terminal_size()[0] - len(prefix) - len(sufix) - 16)
    count = len(it)
    def show(j):
        x = int(size*j/count)
        sys.stdout.write("%s[%s%s] %i ← %i %s  \r" % (prefix, "#"*x, "."*(size-x), j, (count-j), sufix))
        sys.stdout.flush()
    show(0) #This prints the progressbar at 0 progress. Then next for loop renders the rest (stating at 1)
    for i, item in enumerate(it): #This is the 'i' in the comment on the 'def' line
        yield item
        show(i+1)
    sys.stdout.write("\n")
    sys.stdout.flush()

def p(t,r,sym='*'):
    global c
    if stretch_x == True:
        c[int((clock_hight-r*math.cos(t))/2)][int(clock_hight+r*math.sin(t))]=sym
    else:
        c[int(clock_hight-r*math.cos(t))][int(clock_hight+r*math.sin(t))]=sym

def analog_clock(_refresh):
    global c
    global stretch_x
    global clock_hight

    hr_fmt = 12
    stretch_x = True #--> if clock_width is twice that of clock_hight
    min_size = 0.02
    hr_size = 0.01
    clock_width = 50
    clock_hight = 25

    try:
        while True:
            print('\n' * 4)
            c = [[' '] * clock_width for i in range(clock_width)]
            t = time.localtime()
            h = t.tm_hour * 6.283 + t.tm_min / 9.549
            for i in range(999):
                p(i/158.0,24)
                p(h,i*min_size,"▓")
                p(h/hr_fmt,i*hr_size,"█")
                for q in range(12):
                    p(q/1.91,24-i*.005,'•')
            for y in range(clock_hight):
                print(''.join(c[y]))
            print((" "*int(((clock_width/2)-2))) + str(time.localtime().tm_hour).zfill(2) + ":" + str(time.localtime().tm_min).zfill(2))
            if _refresh == True:
                print("\n[ctrl + c] to terminate", end='')
                time.sleep(60)
                clear()
            else:
                break
    except:
        #exit without error message
        return

def mini_clocks(_refresh):
    global c
    global stretch_x
    global clock_hight

    hr_fmt = 12
    stretch_x = True #--> if clock_width is twice that of clock_hight
    min_size = 0.02
    hr_size = 0.01
    clock_width = 26
    clock_hight = 13

    try:
        while True:
            print('\n' * 4)
            c = [[' '] * clock_width for i in range(clock_width)]
            t = time.localtime()
            h = t.tm_hour * 6.283 + t.tm_min / 9.549
            for i in range(999):
                p(i/158.0,24)
                p(h,i*min_size,"▓")
                p(h/hr_fmt,i*hr_size,"█")
                for q in range(12):
                    p(q/1.91,24-i*.005,'•')
            for y in range(clock_hight):
                print(''.join(c[y]))
            print((" "*int(((clock_width/2)-2))) + str(time.localtime().tm_hour).zfill(2) + ":" + str(time.localtime().tm_min).zfill(2))
            if _refresh == True:
                print("\n[ctrl + c] to terminate", end='')
                time.sleep(60)
                clear()
            else:
                break
    except:
        #exit without error message
        return

def cli():
    if args.timer != None:
        countdownTimer(args.timer[0])
    else:
        analog_clock(args._refresh)