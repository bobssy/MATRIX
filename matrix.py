#! /usr/bin/env python3

# Author: Bojidar Georgiev
# bobssy@gmail.com

MAX_CASCADES = 600
MAX_COLS = 20
FRAME_DELAY = 0.03

MAX_SPEED = 5

import shutil, sys, time
from random import choice, randrange, paretovariate

CSI = "\x1b["
pr = lambda command: print("\x1b[", command, sep="", end="")
getchars = lambda start, end: [chr(i) for i in range(start, end)]

black, green, white = "30", "32", "37"

latin = getchars(0x30, 0x80)
greek = getchars(0x390, 0x3d0)
hebrew = getchars(0x5d0, 0x5eb)
cyrillic = getchars(0x400, 0x50)

chars = "ｦｲｸｺｿﾁﾄﾉﾌﾔﾖﾙﾚﾛﾝﾏﾓﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ"

def pareto(limit):
    scale = lines // 2
    number = (paretovariate(1.16) - 1) * scale
    return max(0, limit - number)

def init():
    global cols, lines
    cols, lines = shutil.get_terminal_size()
    pr("?25l")  # Скрива курсора
    pr("s")  # Запазва позицията на курсора

def end():
    pr("m")   # Нулира атрибутите
    pr("2J")  # Изчиства екрана
    pr("u")  # Възстановява позицията на курсора
    pr("?25h")  # Показва курсора

def print_at(char, x, y, color="", bright="0"):
    pr("%d;%df" % (y, x))
    pr(bright + ";" + color + "m")
    print(char, end="", flush=True)

def update_line(speed, counter, line):
    counter += 1
    if counter >= speed:
        line += 1
        counter = 0
    return counter, line

def cascade(col, message_timeout):
    speed = randrange(1, MAX_SPEED)
    espeed = randrange(1, MAX_SPEED)
    line = counter = ecounter = 0
    oldline = eline = -1
    erasing = False
    bright = "1"
    limit = pareto(lines)
    
    # Изчаква timeout преди да позволи изтриването на съобщението
    while True:
        counter, line = update_line(speed, counter, line)
        if randrange(10 * speed) < 1:
            bright = "0"
        if line > 1 and line <= limit and oldline != line:
            print_at(choice(chars), col, line - 1, green, bright)
        if line < limit:
            print_at(choice(chars), col, line, white, "1")
        if erasing:
            if time.time() > message_timeout:  # Позволява изтриването след message_timeout
                ecounter, eline = update_line(espeed, ecounter, eline)
                print_at(" ", col, eline, black)
        else:
            erasing = randrange(line + 1) > (lines / 2)
            eline = 0
        yield None
        oldline = line
        if eline >= limit:
            print_at(" ", col, oldline, black)
            break

def display_message(message):
    """ Показва съобщение в центъра на екрана. """
    x = cols // 2 - len(message) // 2
    y = lines // 2
    pr(f"{y};{x}f")
    pr("1;" + white + "m")
    print(message, end="", flush=True)

def main():
    start_time = time.time()
    cascading = set()
    show_first_message = True
    show_second_message = True

    first_message_duration = 30  # Време преди съобщението да може да бъде изтрито (в секунди)
    second_message_duration = 30  # Време преди второто съобщение да може да бъде изтрито (в секунди)

    # Инициализация на timeout променливи
    message_timeout_1 = start_time
    message_timeout_2 = start_time

    while True:
        elapsed_time = time.time() - start_time

        if elapsed_time >= 10 and show_first_message:
            display_message("THE MATRIX HAS YOU....")
            message_timeout_1 = time.time() + first_message_duration
            show_first_message = False  # Показва само веднъж

        if elapsed_time >= 20 and show_second_message:
            display_message("FOLLOW THE ROAD TO LEFKADA")
            message_timeout_2 = time.time() + second_message_duration
            show_second_message = False  # Показва само веднъж

        # Използване на правилния timeout в зависимост от изминалото време
        if elapsed_time < 20:
            current_timeout = message_timeout_1
        else:
            current_timeout = message_timeout_2

        while add_new(cascading, current_timeout): pass
        stopped = iterate(cascading)
        sys.stdout.flush()
        cascading.difference_update(stopped)
        time.sleep(FRAME_DELAY)

def add_new(cascading, message_timeout):
    if randrange(MAX_CASCADES + 1) > len(cascading):
        col = randrange(cols)
        for i in range(randrange(MAX_COLS)):
            cascading.add(cascade((col + i) % cols, message_timeout))
        return True
    return False

def iterate(cascading):
    stopped = set()
    for c in cascading:
        try:
            next(c)
        except StopIteration:
            stopped.add(c)
    return stopped

def doit():
    try:
        init()
        main()
    except KeyboardInterrupt:
        pass
    finally:
        end()

if __name__ == "__main__":
    doit()
