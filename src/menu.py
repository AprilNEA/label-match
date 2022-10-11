import sys
import tty, termios
from typing import List, AnyStr

CREL_C = '\x03'
DIRECTIION_PREFIX = '\x1b'
UP = '\x1b[A'
DOWN = '\x1b[B'
ENTER = '\r'


def catch_except(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except termios.error as e:
            print(f"Please run script with your terminal, Error:{e}")
            exit()

    return wrapper


def show_choose(choose: List, pos: int) -> None:
    i = 0
    s = ''
    while i < len(choose):
        if i == pos:
            temp = '\033[32;1m >  '
        else:
            temp = '    '
        temp += str(choose[i]) + '\033[0m\n'
        i += 1
        s += temp
    s += '\n'
    sys.stdout.write(s)
    sys.stdout.flush()


def clear_choose(choose: List) -> None:
    sys.stdout.write('\033[%dA\033[K' % (len(choose) + 1,))
    sys.stdout.flush()


def get_input() -> AnyStr:
    ch = sys.stdin.read(1)
    if ch == DIRECTIION_PREFIX:
        ch += sys.stdin.read(2)
    return ch


def show_menu(choose: List, title=None, pos=0, is_first=True):
    if title and is_first:
        sys.stdout.write(title + '\n')
        sys.stdout.flush()
    if not is_first:
        clear_choose(choose)

    show_choose(choose, pos)


@catch_except
def tty_menu(choose, title=None) -> int:
    pos = 0

    show_menu(choose, title, pos)

    while True:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = get_input()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        if key == CREL_C:
            break
        elif key == ENTER:
            return pos
        elif key == UP:
            pos -= 1
        elif key == DOWN:
            pos += 1

        if pos < 0:
            pos = len(choose) - 1
        elif pos >= len(choose):
            pos = 0
        show_menu(choose, title, pos, False)
